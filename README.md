<!-- PROJECT LOGO -->
<br />
<div align="center">
  </a>

  <h3 align="center">SpikeTool3</h3>

  <p align="center">
    A tool for the curation of time plots (e.g. from calcium imaging)
    <br />
    ·
    <a href="https://github.com/GabStoelting/SpikeTool3/issues">Report Bug</a>
    ·
    <a href="https://github.com/GabStoelting/SpikeTool3/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#citations">Citations</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

This project was started to allow for the curation of calcium imaging recordings using intensiometric and ratiometric dyes. It extended to allow for the selection of calcium spikes and 
the definition of perfusion conditions.
Versions of this software have been used in:
<p align="right">(<a href="#top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

This tool is written in python and will likely work with any version of python > 3.6. I recommend using <a href="https://www.anaconda.com/products/individual">Anaconda</a> or <a href="https://docs.conda.io/en/latest/miniconda.html">Miniconda</a> but this is no hard requirement. However, for the installation instructions below, I'll assume that you are able to use the conda package manager.

### Prerequisites

This tool requires python>3.6, numpy, pandas, h5py, matplotlib and tkintertable libraries. 

### Installation

Please follow these steps:

1. Clone the repository using command line tools (below) or by using a GUI version of Git
   ```sh
   git clone https://github.com/GabStoelting/SpikeTool3
   ```
2. Install the required libraries via conda
   ```sh
   conda install numpy
   conda install pandas
   conda install h5py
   conda install matplotlib
   conda install pip
   ```
3. Install tkintertable via pip (not available via conda)
   ```sh
   pip install tkintertable
   ```

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

You can start the tool by running
```sh
python GUImain.py
```
or, if running on Windows, by editing the SpikeTool.bat to reflect the paths setup on your machine.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [ ] Make installation easier
- [ ] Enhance spike-finding algorithm
- [x] Add ability to merge projects

See the [open issues](https://github.com/GabStoelting/SpikeTool3/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- CITATIONS -->
## Citations

This tool has been used in the following publications:
<ol>
  <li>
    <a href="https://www.pnas.org/content/118/17/e2014876118">
      Seidel, E. et al. Enhanced Ca2+ signaling, mild primary aldosteronism, and hypertension in a familial hyperaldosteronism mouse model (Cacna1hM1560V/+). PNAS 118, (2021).
    </a>
  </li>
  <li>
    <a href="https://www.nature.com/articles/s41467-019-13033-4">
      Schewe, J. et al. Elevated aldosterone and blood pressure in a mouse model of familial hyperaldosteronism with ClC-2 mutation. Nature Communications 10, 5155 (2019).
    </a>
  </li>
</ol>


<!-- LICENSE -->
## License

Distributed under the GPL 3.0 License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Gabriel Stölting - gabriel.stoelting@bih-charite.de
Project Link: [https://github.com/GabStoelting/SpikeTool3](https://github.com/GabStoelting/SpikeTool3)

<p align="right">(<a href="#top">back to top</a>)</p>
