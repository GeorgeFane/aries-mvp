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

## Commit Descriptions

### April 2

Whipped up a few more HTML files (templates) for the MVP. Now it has the whole flow for the DIDPal app: login page, FSP partners list, create account pages, thank you page. 'Create account' includes input fresh info and present held creds.

Removed the faux subwallet system and ignored [multitenancy](https://github.com/hyperledger/aries-cloudagent-python/blob/main/Multitenancy.md). Each DIDPal app will be one Alice agent, and each FSP will run one node/Faber agent, perhaps with multitenancy. I say 'perhaps' because each Faber agent can send ~5.4 credentials per second, which probably handles more than one customer per second. PayPal estimates that it gains a customer every second, which, if true for other FSPs, is manageable for Aries.

Side note: Faber and Alice each recieve a new individual DID for each connection, even with the same agent. Imagine the same Faber and Alice connect five times; they each recieve five new DIDs. While a pseudonym is expected to be (Name, DID), it might have to be (Name, [DID List]).

This is like my old version, where it looked nice but called a self-built API's endpoints. That merely imitated the Aries Open API; this version uses it. It also has logging in the console.

Next step is to make the MVP look better, following PayPal's design styles.
