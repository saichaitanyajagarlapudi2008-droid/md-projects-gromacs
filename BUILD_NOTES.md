# GROMACS builds on Apple Silicon (macOS)

Notes on the three GROMACS 2026.3 builds on my MacBook (Apple A18 Pro: 2 performance + 4 efficiency cores, Apple GPU via OpenCL), why each one exists, and every problem I hit while building them. Built 6 November 2026.

All commands are written for zsh and contain no `#` comments, because zsh does not treat `#` as a comment when typed at the prompt (unless you run `setopt interactivecomments`).

## Overview

| Build | Install folder | Program | Compiler | Precision | Parallelism | Extras | Use for |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1. Original | `/opt/gromacs` | `gmx` | GCC 16 (Homebrew) | mixed | thread-MPI + OpenMP, OpenCL GPU | PLUMED, Colvars | Ongoing PVC/DEHP series (keep one build per dataset) |
| 2. Clang + Torch | `~/gromacs-nnp` | `gmx` | Apple clang 21 | mixed | thread-MPI + OpenMP, OpenCL GPU | LibTorch 2.15 (neural-network potentials), PLUMED, Colvars | New classical MD (about 20% faster than build 1), ML potentials |
| 3. QM/MM | `~/gromacs-qmmm-clang` | `gmx_mpi_d` | Apple clang 21 (via Open MPI) | double | real MPI + OpenMP, CPU only | CP2K 2026.2 (QM/MM) | QM/MM runs |

Choose a build in each terminal by sourcing its `GMXRC`:

```bash
source /opt/gromacs/bin/GMXRC
source ~/gromacs-nnp/bin/GMXRC
source ~/gromacs-qmmm-clang/bin/GMXRC
```

`gmx --version` (or `gmx_mpi_d --version`) prints which compiler, GPU backend and extras a build has. The same block appears at the top of every `md.log`.

## Prerequisites (Homebrew)

```bash
brew install cmake fftw libomp open-mpi openblas pkgconf gcc cp2k
```

Versions used: CMake 4.4.1, FFTW 3.3.11, libomp 23, Open MPI 5.0.11, OpenBLAS 0.3.34, GCC 16.2, CP2K 2026.2. Xcode command-line tools provide Apple clang (`xcode-select -p` shows `/Library/Developer/CommandLineTools`).

Before building anything, close all conda environments (`conda deactivate` until no `(base)` or `(plumed)` prefix is left), so CMake does not pick up conda's compilers or libraries.

GROMACS source: `~/gromacs_build/gromacs-2026.3`. Each build has its own build folder inside it.

## Build 1: original (GCC)

Already existed. From `gmx --version`: GCC 16 (`/opt/homebrew/bin/gcc-16`), OpenCL GPU, VkFFT for the GPU, FFTW 3.3.10 on the CPU, PLUMED and Colvars enabled, CP2K and Torch disabled. Build folder: `~/gromacs_build/gromacs-2026.3/build`.

## Build 2: Apple clang + LibTorch

### Why a separate build

The prebuilt LibTorch for macOS is compiled with Apple clang and its C++ standard library (libc++). Build 1 uses GCC and libstdc++. The GROMACS install guide says LibTorch must use the same C++ ABI as the rest of GROMACS, so Torch support needs a clang build.

### 1. Get LibTorch

From pytorch.org/get-started/locally: Stable, Mac, LibTorch, C++/Java, Default.

```bash
cd ~
curl -L -o libtorch-macos-arm64-2.15.0.zip https://download.pytorch.org/libtorch/cpu/libtorch-macos-arm64-2.15.0.zip
unzip -q libtorch-macos-arm64-2.15.0.zip
mv libtorch libtorch-2.15.0
rm libtorch-macos-arm64-2.15.0.zip
```

The version is in the folder name because a neural-network model must be run with the same LibTorch version it was exported with.

### 2. Configure and build

```bash
cd ~/gromacs_build/gromacs-2026.3
mkdir -p build-nnp && cd build-nnp
CC=clang CXX=clang++ cmake .. \
  -DCMAKE_INSTALL_PREFIX=$HOME/gromacs-nnp \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_CXX_STANDARD=20 \
  -DGMX_GPU=OpenCL \
  -DGMX_FFT_LIBRARY=fftw3 \
  -DCMAKE_PREFIX_PATH="$HOME/libtorch-2.15.0;/opt/homebrew/opt/fftw" \
  -DGMX_NNPOT=TORCH \
  -DOpenMP_C_FLAGS="-Xpreprocessor -fopenmp -I/opt/homebrew/opt/libomp/include" \
  -DOpenMP_CXX_FLAGS="-Xpreprocessor -fopenmp -I/opt/homebrew/opt/libomp/include" \
  -DOpenMP_C_LIB_NAMES=omp \
  -DOpenMP_CXX_LIB_NAMES=omp \
  -DOpenMP_omp_LIBRARY=$HOME/libtorch-2.15.0/lib/libomp.dylib \
  -DCMAKE_INSTALL_RPATH_USE_LINK_PATH=ON \
  2>&1 | tee cmake-nnp.log | tail -5
make -j 6 2>&1 | tee build-nnp.log | tail -3
make install
```

What the flags do:

- `CMAKE_CXX_STANDARD=20`: LibTorch 2.15 headers need C++20. GROMACS defaults to C++17 but officially supports C++20.
- OpenMP flags: Apple clang ships without OpenMP. The headers come from Homebrew's libomp, but the library linked is LibTorch's own `libomp.dylib`, so only one OpenMP runtime is ever loaded in the process.
- `CMAKE_INSTALL_RPATH_USE_LINK_PATH=ON`: the installed `gmx` remembers where the LibTorch libraries are.
- OpenCL works with any host compiler: the library is part of macOS (`OpenCL.framework`), and the GPU kernels are compiled by Apple's OpenCL driver when `mdrun` starts.

### 3. Fix the OpenMP library path (needed after every `make install`)

LibTorch's `libomp.dylib` still carries the path of the PyTorch build machine (`/opt/llvm-openmp/lib/libomp.dylib`), so the installed `gmx` fails with `Library not loaded`. Rewrite the path and re-sign (Apple Silicon refuses to run modified binaries that are not re-signed):

```bash
for f in ~/gromacs-nnp/bin/gmx ~/gromacs-nnp/lib/*.dylib; do
  if otool -L "$f" | grep -q /opt/llvm-openmp; then
    install_name_tool -change /opt/llvm-openmp/lib/libomp.dylib $HOME/libtorch-2.15.0/lib/libomp.dylib "$f"
    codesign --force -s - "$f"
    echo "fixed: $f"
  fi
done
```

### 4. Check

```bash
source ~/gromacs-nnp/bin/GMXRC
gmx --version | grep -E "Torch support|GPU support|C\+\+ compiler:"
```

Expected: `Torch support: enabled (version 2.15.0)`, `GPU support: OpenCL`, `AppleClang 21`.

Validation: the same `.tpr` (DSPC Martini bilayer) gave identical step-0 energies in builds 1 and 2 (Bond 1990.53, Angle 1345.28, LJ −46843.7, Coulomb −511.71 kJ/mol).

## Build 3: QM/MM with CP2K (clang + MPI)

### Why this works on a Mac

Homebrew's CP2K 2026.2 already includes the library GROMACS needs: `libcp2k.dylib`, the header `libcp2k.h`, and a pkg-config file `libcp2k.pc`. Building CP2K from source was not needed.

The GROMACS install guide asks for:

- CP2K 8.1 or newer, linked as libcp2k
- a static GROMACS build (`BUILD_SHARED_LIBS=OFF`, `GMXAPI=OFF`, `GMX_INSTALL_NBLIB_API=OFF`)
- double precision recommended
- the same FFT, BLAS and LAPACK libraries in CP2K and GROMACS

Homebrew's CP2K is the MPI version (`cp2k.psmp`), so GROMACS uses the same Open MPI. Double precision means no GPU.

### 1. Fix Homebrew's broken `libcp2k.pc`

Homebrew's file has a doubled path:

```
libdir="${prefix}//opt/homebrew/Cellar/cp2k/2026.2/lib"
```

Make a corrected copy and point GROMACS at it. Homebrew's own file is left untouched.

```bash
mkdir -p ~/cp2k-pc/pkgconfig
sed 's#^libdir=.*#libdir="${prefix}/lib"#' /opt/homebrew/lib/pkgconfig/libcp2k.pc > ~/cp2k-pc/pkgconfig/libcp2k.pc
PKG_CONFIG_PATH=$HOME/cp2k-pc/pkgconfig pkg-config --cflags --libs libcp2k
```

The last line should show `-L/opt/homebrew/Cellar/cp2k/2026.2/lib -lcp2k`. GROMACS's CMake looks for `libcp2k.pc` in `${CP2K_DIR}/pkgconfig`, so `CP2K_DIR=$HOME/cp2k-pc` below.

### 2. Configure and build

```bash
export OMPI_CC=clang OMPI_CXX=clang++ OMPI_FC=gfortran-16
cd ~/gromacs_build/gromacs-2026.3
mkdir -p build-qmmm-clang && cd build-qmmm-clang
CC=mpicc CXX=mpicxx cmake .. \
  -DCMAKE_INSTALL_PREFIX=$HOME/gromacs-qmmm-clang \
  -DCMAKE_BUILD_TYPE=Release \
  -DGMX_MPI=ON \
  -DGMX_DOUBLE=ON \
  -DGMX_GPU=OFF \
  -DGMX_NNPOT=OFF \
  -DBUILD_SHARED_LIBS=OFF -DGMXAPI=OFF -DGMX_INSTALL_NBLIB_API=OFF \
  -DGMX_FFT_LIBRARY=fftw3 \
  -DCMAKE_PREFIX_PATH=/opt/homebrew/opt/fftw \
  -DGMX_BLAS_USER=/opt/homebrew/opt/openblas/lib/libopenblas.dylib \
  -DGMX_LAPACK_USER=/opt/homebrew/opt/openblas/lib/libopenblas.dylib \
  -DOpenMP_C_FLAGS="-Xpreprocessor -fopenmp -I/opt/homebrew/opt/libomp/include" \
  -DOpenMP_CXX_FLAGS="-Xpreprocessor -fopenmp -I/opt/homebrew/opt/libomp/include" \
  -DOpenMP_C_LIB_NAMES=omp \
  -DOpenMP_CXX_LIB_NAMES=omp \
  -DOpenMP_omp_LIBRARY=/opt/homebrew/opt/libomp/lib/libomp.dylib \
  -DGMX_CP2K=ON \
  -DCP2K_DIR=$HOME/cp2k-pc \
  2>&1 | tee cmake.log | grep -E "Found libcp2k|Found OpenMP|Configuring done|Error"
make -j 6 2>&1 | tee build.log | tail -3
make install
```

What the less obvious parts do:

- `OMPI_CC=clang …`: makes Open MPI's `mpicc`/`mpicxx` wrappers use Apple clang. `OMPI_FC=gfortran-16` keeps Fortran on GCC, because GROMACS links Open MPI's Fortran library for CP2K.
- OpenMP flags: link Homebrew's `libomp`, the same file CP2K and OpenBLAS use. One OpenMP runtime for everything (see "Problems" below for why this matters).
- `GMX_NNPOT=OFF`: otherwise CMake finds Homebrew's PyTorch in `/opt/homebrew/include` and fails with C++20 errors.
- The program is named `gmx_mpi_d` (MPI, double precision).

### 3. Check

```bash
source ~/gromacs-qmmm-clang/bin/GMXRC
gmx_mpi_d --version | grep -E "Precision|MPI library|CP2K support"
otool -L ~/gromacs-qmmm-clang/bin/gmx_mpi_d | grep -i -E "gomp|libomp|cp2k"
```

Expected: `Precision: double`, `MPI library: MPI`, `CP2K support: enabled (version CP2K version 2026.2)`, and `otool` showing `libcp2k` and `libomp` but no `libgomp`.

### 4. Test system (one QM water in 109 SPC/E waters)

`qmmm.mdp`:

```
integrator               = md
dt                       = 0.0005
nsteps                   = 20
nstcalcenergy            = 1
nstenergy                = 1
nstlog                   = 1
cutoff-scheme            = Verlet
coulombtype              = PME
rcoulomb                 = 0.7
rvdw                     = 0.7
tcoupl                   = no
pcoupl                   = no
define                   = -DFLEXIBLE
constraints              = none
gen-vel                  = yes
gen-temp                 = 300
qmmm-cp2k-active         = true
qmmm-cp2k-qmgroup        = QMatoms
qmmm-cp2k-qmmethod       = PBE
qmmm-cp2k-qmcharge       = 0
qmmm-cp2k-qmmultiplicity = 1
```

Topology: OPLS-AA `spce.itp`. Index group `QMatoms` = atoms 1 2 3. Flexible water and a 0.5 fs step, because the QM water's bonds must be free.

Run:

```bash
OMP_NUM_THREADS=6 mpirun -np 1 gmx_mpi_d mdrun -deffnm qmmm
```

Result: the energy table includes `Quantum En.` = −45,143 kJ/mol = −17.19 Ha. Standalone CP2K (PBE, DZVP-MOLOPT-SR-GTH, GTH-PBE, 300 Ry) for one water gives −17.2198 Ha, so the coupling is consistent.

## PLUMED

Build 1 and build 2 contain the PLUMED interface, but the PLUMED library itself is separate. GROMACS loads it through the `PLUMED_KERNEL` environment variable.

```bash
conda create -n plumed -c conda-forge plumed -y
conda activate plumed
echo "export PLUMED_KERNEL=$CONDA_PREFIX/lib/libplumedKernel.dylib" >> ~/.zshrc
```

Run with `gmx mdrun ... -plumed plumed.dat`. The docs say PLUMED does not work with more than one thread-MPI rank, so do not use `-ntmpi` above 1.

## Problems hit and how they were fixed

| Problem | Symptom | Cause | Fix |
| --- | --- | --- | --- |
| zsh comments | `Ignoring extra path from command line: "flags"` | zsh passes `# text` as arguments at the prompt | No `#` comments in pasted commands, or `setopt interactivecomments` |
| Placeholders | `zsh: parse error near '\n'` | `<name>` is read as a file redirection | Always use real names in commands |
| Wrong folder | `source directory "/Users" does not appear to contain CMakeLists.txt` | `cmake ..` run from the home folder | Run `cmake ..` from inside a build folder in the source tree |
| LibTorch needs C++20 | `C++20 or later compatible compiler is required to use PyTorch`, then errors about `std::bit_width`, `strong_ordering`, `requires` | GROMACS defaults to C++17 | `-DCMAKE_CXX_STANDARD=20` |
| LibTorch's libomp path | `dyld: Library not loaded: /opt/llvm-openmp/lib/libomp.dylib` | libomp keeps the PyTorch build machine's path | `install_name_tool -change` + `codesign --force -s -` |
| Broken `libcp2k.pc` | (would give "library not found for -lcp2k") | Homebrew writes a doubled `libdir` path | Corrected copy in `~/cp2k-pc/pkgconfig` |
| Homebrew PyTorch picked up | C++20 errors from `/opt/homebrew/include/torch` in `colvars_objlib` | GROMACS enables Torch automatically when it finds it | `-DGMX_NNPOT=OFF` |
| Two OpenMP runtimes | Segfault in CP2K `ortho_cxyz_to_grid` inside an OpenMP worker thread with more than 1 thread; fine with 1 thread | GCC-built GROMACS uses `libgomp`, Homebrew CP2K uses LLVM `libomp`. Not a stack-size problem: `OMP_STACKSIZE=256M` still crashed, and standalone CP2K ran fine with 6 threads | Rebuild GROMACS with clang + Homebrew `libomp`, so the whole process uses one runtime |
| GROMACS without OpenMP | `More than 1 OpenMP thread requested, but GROMACS was compiled without OpenMP` and `Environment variable OMP_NUM_THREADS ... and the number of threads requested` | GROMACS reads the same `OMP_NUM_THREADS` as CP2K and refuses a mismatch | Not usable for threads; solved by the clang rebuild above |

Not attempted: CP2K GPU acceleration. According to the CP2K manual, OpenCL only accelerates DBCSR/DBM, not the GRID or PW backends, and macOS is not covered.

## Performance

Classical, Martini 3 DSPC bilayer (2,304 beads), 500 ps test:

| Build | ns/day |
| --- | --- |
| 1. GCC | 3,944 |
| 2. Apple clang | 4,771 |

QM/MM, one QM water, 20 steps (ms per step, lower is better):

| Build and layout | ms/step | 1 ns would take |
| --- | --- | --- |
| GCC, 1 process × 1 thread | 14,001 | about 324 days |
| GCC, 6 processes × 1 thread | 6,282 | about 146 days |
| Clang, 6 × 1 | 5,330 | |
| Clang, 3 × 2 | 4,653 | |
| Clang, 2 × 3 | 5,240 | |
| Clang, 1 process × 6 threads | 4,493–4,959 | about 104–115 days |

Rules learned:

- Processes × threads must not exceed the number of cores (6 here). More causes oversubscription and slows everything down.
- The A18 Pro has 2 fast and 4 slow cores, so work split six ways is held back by the slow cores.
- In classical MD on this Mac the CPU is the bottleneck (`GPU/CPU evaluation time ratio` about 0.04 in `md.log`), so CPU-side improvements (compiler, OpenMP runtime) show up directly in ns/day.
- QM/MM is for short runs: a few picoseconds at about 2–3 hours per ps.

## Maintenance

- `brew pin cp2k`: build 3 links `libcp2k.2026.2.dylib` by its versioned name. A CP2K upgrade would break it until GROMACS is rebuilt.
- After any `make install` of build 2, run the `install_name_tool` loop again.
- Homebrew's `libomp` is linked through `/opt/homebrew/opt/libomp`, which survives normal upgrades.
- To make build 2 the default everywhere (after the PVC/DEHP series is finished): `echo 'source ~/gromacs-nnp/bin/GMXRC' >> ~/.zshrc`

## Sources

- GROMACS 2026 install guide: building with CP2K QM/MM support, building with neural network potential support, PLUMED, hwloc, macOS OpenMP notes (`docs/install-guide/index.rst` in the GROMACS source)
- GROMACS reference manual: QM/MM with CP2K, neural network potentials, using PLUMED
- GROMACS `cmake/gmxManageCP2K.cmake` (how `CP2K_DIR` and pkg-config are used)
- GROMACS forum: "QM/MM with new CP2K 2026.1" (CP2K now builds only a shared libcp2k)
- CP2K manual: OpenCL acceleration
