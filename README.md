# IoTDB Cloud

This is a proof of concept for a self service hosted IoTDB Cloud Solution.
The basic Idea is to get a Service like MongoDBs Atlas but for timeseries based on IoTDB.

## Functionality

The general idea is to have a setup where new Apache IoTDB instances can be created by users or interested parties.
Current Implementation allows to create an IoTDB Instance with a single click.
In the background in Kubernetes the following ressources are created:

* IoTDB Single Node Instance (as stateful set with PVC for data)
* Corresponding Headless Service
* Service which exposes IoTDB as External IP
* Initializer Job to configure the IoTDB instance (currently only set password)

## Look and Feel

![Screenshot](docs/images/screenshot1.png)

## Roadmap

- [X] First prototyp
- [ ] User Login
- [ ] Rich Settings for Instance creation
- [ ] Move Async Tasks to Celery
- [ ] Limit Demo Accounts for Users
- [ ] Send Email when instance is ready
- [ ] Use TCP with Ingress to reduce external IPs that are needed