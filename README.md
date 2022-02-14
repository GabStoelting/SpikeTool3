# SpikeTool3
#
# README template based on https://github.com/othneildrew/Best-README-Template/blob/master/README.md 


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
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
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
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

This project was started to allow for the curation of calcium imaging recordings using intensiometric and ratiometric dyes. It extended to allow for the selection of calcium spikes and 
the definition of perfusion conditions.

<p align="right">(<a href="#top">back to top</a>)</p>



### Built With

This section should list any major frameworks/libraries used to bootstrap your project. Leave any add-ons/plugins for the acknowledgements section. Here are a few examples.

* [Next.js](https://nextjs.org/)
* [React.js](https://reactjs.org/)
* [Vue.js](https://vuejs.org/)
* [Angular](https://angular.io/)
* [Svelte](https://svelte.dev/)
* [Laravel](https://laravel.com)
* [Bootstrap](https://getbootstrap.com)
* [JQuery](https://jquery.com)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

This tool is written in python and will likely work with any version of python > 3.6. I recommend using Anaconda or Miniconda but this is no hard requirement. However,
for the examples below, I'll assume that you are able to use the conda package manager.

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.
* npm
  ```sh
  npm install npm@latest -g
  ```

### Installation

Please follow these steps:

1. Clone the repository using command line tools (below) or by using a GUI version of Git
   ```sh
   git clone https://github.com/your_username_/Project-Name.git
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
- [ ] Add ability to merge projects

See the [open issues](https://github.com/GabStoelting/SpikeTool3/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- LICENSE -->
## License

Distributed under the GPL 3.0 License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Gabriel Stölting - gabriel.stoelting@bih-charite.de
Project Link: [https://github.com/GabStoelting/SpikeTool3](https://github.com/GabStoelting/SpikeTool3)

<p align="right">(<a href="#top">back to top</a>)</p>
