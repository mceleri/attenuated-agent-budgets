# Attenuated Agent Budgets

Exploring cryptographic budget delegation (biscuits) for multi-agent M2M payments. 🚧 Work in progress. 🚧

## What this is

A whitepaper-in-progress exploring how a single, fiat-settled payment (via a Merchant of Record) can be turned into a granular, revocable, offline-attenuable budget for a swarm of autonomous sub-agents, without requiring cryptocurrency, wallets, or per-transaction settlement.

The starting observation: current M2M payment protocols (L402, X402, MPP) either assume crypto-native settlement or per-request autonomous payment, both of which are impractical for freelancers and SMEs operating under many tax regimes, where every crypto-denominated microtransaction could become a taxable disposal event. This project explores what happens once you accept that constraint and ask: how do you still give an agent swarm fine-grained, independently revocable spending control over a budget that was paid for as a single transaction via a Merchant of Record?

This is a niche exploration, not a claim to revolutionize agent payments. It's being built and written in the open, incrementally, with open problems tracked explicitly rather than hidden.

## Status

🚧 Active specification and reference implementation. The architectural model, wire protocol, legal analysis, open problems, and an executable reference implementation in Python are in place. Follow along via commits and releases. 

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

## Why open, incremental, and public

This repo is being developed in public on purpose: to get early feedback, to document the reasoning behind design changes (including reversals), and to keep a honest, versioned record of what's solved versus what's still an open problem. Tags mark meaningful milestones (`v0.1-abstract`, `v0.2-architecture`, ...).

## License

This repository uses a dual license:
- **Text and documentation** (the whitepaper itself): [CC-BY-4.0](./LICENSE) reuse and adaptation welcome, with attribution.
- **Code examples** (`examples/`): [MIT](./examples/LICENSE) use freely.

## Get in touch

If you're working on similar problems (agent payments, budget delegation, or M2M infrastructure more broadly) I'd like to hear from you. Open an issue, or find me on [LinkedIn](https://www.linkedin.com/in/marco-celeri-61730b55).
