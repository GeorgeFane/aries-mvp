# Aries MVP

This MVP builds on Hyperledger's Aries-Cloudagent-Python sample to use verifiable credentials in a specific context

## Setup

Necessary clones and checkout compatible version of Aries sample

```bash
git clone https://github.com/GeorgeFane/aries-mvp

git clone https://github.com/hyperledger/aries-cloudagent-python

cd aries-cloudagent-python

git checkout -b b9c59da5a6d0482d63ab60e6b3c184b864b8a6f0

cd
```

## Run

In one console:

```bash
source \ ~/envs/hello_world/bin/activate

cd aries-cloudagent-python/demo

LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run_demo faber
```

In another console:

```bash
source \ ~/envs/hello_world/bin/activate

cd aries-cloudagent-python/demo

LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run_demo faber
```

In a third console:

```bash
source \ ~/envs/hello_world/bin/activate

cd aries-mvp

python main.py
```

## Further Development

Prettier interface

HTML web form validation

Descriptive logging in console