# Banchi (番地)

A web application for managing static IP addresses on a private network.

## Purpose

Banchi is meant to handle allocating IP addresses for boxes on a network based on
requirements for vlans of the box and allow a universal interface for retrieving
the information for various reasons.

## API

Banchi uses a RESTful API with the various endpoints being defined via the JSON
response for the root route.  Everything should be discoverable from these routes.

## Future

### CLI

There is a planned CLI that allows for most of the operations to be performed via
the command line, either through single commands or by dropping into a subshell
that allows for step by step operations.

### Hiera backend

A backend for the hiera lookup system used by Puppet to allow for the information
allocation to be used within puppet without having to generate large data files.

### Web frontend

A web frontend to allow for a more graphical/dashboard like interaction with the
data, including visualizations or more complex operations.

### DNS server

Have the application act as a DNS server using the requesting IP to determine which
IP endpoint to return for a requested hostname (so a request from one vlan will
return the corresponding IP for the hostname on that vlan, and a request from 
another vlan will return a different IP associated with its vlan).
