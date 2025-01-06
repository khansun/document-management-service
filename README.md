# DMS

Papermerge DMS or simply Papermerge is a open source document management system
designed to work with scanned documents (also called digital archives). It
extracts text from your scans using OCR, indexes
them, and prepares them for full text search. Papermerge provides the look and feel
of modern desktop file browsers. It has features like dual panel document
browser, drag and drop, tags, hierarchical folders and full text search so that
you can efficiently store and organize your documents.

It supports PDF, TIFF, JPEG and PNG document file formats.
Papermerge is perfect tool for long term storage of your documents.

## Features Highlights

* Web UI with desktop like experience
* OpenAPI compliant REST API
* Works with PDF, JPEG, PNG and TIFF documents
* OCR (Optical Character Recognition) of the documents
* OCRed text overlay (you can download document with OCRed text overlay)
* Full Text Search of the scanned documents
* Document Versioning
* Tags - assign colored tags to documents or folders
* Documents and Folders - users can organize documents in folders
* Document Types
* Custom Fields (metadata) per document type
* Multi-User
* Page Management - delete, reorder, cut, move, extract pages



## Documentation

Papermerge DMS documentation is available at [https://docs.papermerge.io](https://docs.papermerge.io/)

# Development build

## Anaconda Environment
* `conda env create -f .\conda-env.yml`
* `poetry install -E pg`
* `.\run.dev.ps1`


# Production build

## Docker Build
* `docker build -t dms-api:dev .`
* `docker image save dms-api:dev -o .\dms-api.tar`

## Docker Compose

* `docker compose up -d`

Open your web browser and point it to http://localhost:12000.

## Ansible Playbook

In order to deploy Papermerge on remote production machine (homelab VM, or cloud VPS instance)
use following [Ansible Playbook](https://github.com/papermerge/ansible).

## Tests

    poetry install
    poetry shell
    pytest tests/

## Linting

Use following command to make sure that your code is formatted per PEP8 spec:

    poetry run task lint
