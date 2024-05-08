# P2P File Transfer System

## Overview

This project implements a peer-to-peer (P2P) file transfer system designed to identify other clusters and facilitate the transfer of files between them. It operates within a distributed network environment, allowing each cluster to dynamically discover peers and request files.

## Features

- **Dynamic Cluster Discovery**: Discovers other clusters dynamically and manages connections between them.
- **File Transfer**: Enables secure file transfers between identified clusters within the network.
- **Configurable Cluster Setup**: Each cluster is set up with its own configuration file and directory, containing a list of peer clusters and any files to be shared.

## Setup

### Creating Cluster Configurations

1. **Create a Directory for Each Cluster**: Each cluster should have its own directory. This directory will contain both the configuration file and any files that are to be shared with other clusters.
2. **Create a Configuration File**: Inside the cluster's directory, create a text file named after the cluster. This file should contain a list of other clusters, formatted as follows:
   ```
   cluster1p[port1],cluster2p[port2],...
   ```

### Starting the System

1. **Identify the Cluster**: When launching the program, you must specify which cluster it represents. This is done by passing the cluster's name as an argument to the script.
2. **Initiate Discovery Messages**: Upon startup, the system begins by sending discovery messages to the clusters listed in the configuration file.
3. **Request Files**: After discovering peers, the cluster can request files from other clusters listed in its configuration.

## Usage

To start the system, ensure that each cluster's directory and configuration file are set up correctly. Then, run the main script with the cluster's name as an argument. The system will handle the rest, from discovery to file transfer.

## Dependencies

- Python 3.x
- socket library (built-in)

## Contribution

Contributions are welcome! Please fork this repository and submit pull requests to enhance functionalities or fix bugs. You can also raise issues for any bugs found or features suggested.

---

This README provides a clearer picture of the functionality and usage of your P2P file transfer system. If there are any other aspects of your project you’d like to highlight or adjust, just let me know!
