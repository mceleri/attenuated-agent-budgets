# Attenuated Agent Budgets

Cryptographic budget delegation (Biscuits) for multi-agent M2M payments via Merchant of Record fiat settlement.

## Overview

This repository documents a specification and reference architecture exploring how a single, fiat-settled payment (via a Merchant of Record) can be turned into a granular, revocable, offline-attenuable budget for a swarm of autonomous sub-agents, without requiring cryptocurrency, wallets, or per-transaction settlement.

### The Problem

Current M2M payment protocols (such as L402, X402, and MPP) generally assume crypto-native settlement or autonomous per-request payments. Both models present severe tax and accounting barriers for freelancers and SMEs under European tax regimes, where every crypto-denominated microtransaction risks triggering a taxable disposal event with heavy reporting overhead.

This project addresses those constraints directly: how to provide an autonomous agent swarm with fine-grained, independently revocable spending authorization over a budget provisioned through standard fiat payment rails.

## Status

Active specification and reference implementation. The core cryptographic architecture, X402 wire protocol, EU tax analysis (SPV classification), open problems, and an executable reference implementation in Python are complete.

## Contents

| File | Description |
|---|---|
| [`00-abstract.md`](./00-abstract.md) | Abstract and problem framing |
| [`01-landscape.md`](./01-landscape.md) | Comparative landscape of M2M payment and discovery protocols (L402, X402, MPP, MoR platforms) |
| [`02-architecture.md`](./02-architecture.md) | Biscuit authorization architecture, Datalog semantics, sealing, and state delegation |
| [`03-wire-protocol.md`](./03-wire-protocol.md) | X402 wire protocol, JSON Schemas, HTTP status code matrix, and concrete wire exchange traces |
| [`04-tax-and-legal.md`](./04-tax-and-legal.md) | Legal disclaimer, EU Voucher Directive analysis (SPV vs. MPV), and tax neutrality |
| [`05-open-problems.md`](./05-open-problems.md) | Technical limitations, concurrency bottlenecks, edge synchronization, and open questions |
| [`06-references.md`](./06-references.md) | Academic, industry standard, and statutory references |
| [`examples/`](./examples/) | Minimal runnable reference implementation (issuance, offline attenuation, hold/capture, verification) |

### Running the Reference Demo

A self-contained Python reference implementation demonstrating all protocol phases (issuance, offline attenuation, fixed-cost calls, dynamic two-phase hold/capture, budget top-up, and surgical revocation) is available in `examples/`:

```bash
cd examples
pip install -r requirements.txt
python3 demo.py
```

## License

This repository uses a dual license:
- **Text and documentation**: [CC-BY-4.0](./LICENSE)
- **Code examples**: [MIT](./examples/LICENSE)

## Get in touch

If you are working on agent payments, budget delegation, or M2M infrastructure, feel free to open an issue or connect on [LinkedIn](https://www.linkedin.com/in/marco-celeri-61730b55).
