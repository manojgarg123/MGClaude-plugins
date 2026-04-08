# MGClaude Plugins

A growing collection of productivity plugins for [Claude](https://claude.ai) — built for real workflows, not demos.

These plugins extend Claude with skills for HR, recruiting, knowledge work, and more. Each one is self-contained and can be installed individually.

---

## Getting Started

### Add this marketplace to Claude

```bash
claude plugin marketplace add MGClaude/MGClaude-plugins
```

Once added, all plugins below are available to install directly.

### Install a specific plugin

```bash
claude plugin install MGClaude/MGClaude-plugins/resume-shortlisting
```

Or install the `.plugin` file directly in Claude Cowork by dragging it into the app.

---

## Plugins

### 🔍 Resume Shortlisting
**Screen and rank candidates against a job description — consistently, at scale.**

Builds a scoring rubric from your JD, evaluates each resume across Skills, Experience, Education, and Fit, and delivers a ranked Excel tracker + HTML dashboard. Skips already-processed resumes so it's safe to re-run as new applications arrive.

📁 [`resume-shortlisting/`](./resume-shortlisting) · [README](./resume-shortlisting/README.md)

---

## Philosophy

Each plugin here is designed to:

- **Work out of the box** — minimal setup, no configuration files to fiddle with
- **Be re-runnable** — safe to use multiple times on the same data without duplication
- **Stay transparent** — Claude explains what it's doing at every step
- **Respect your data** — nothing leaves your machine unless you explicitly connect an external service

---

## Requests & Contributions

Have a workflow you'd like to see automated? Open an [issue](../../issues) describing the use case.

Pull requests are welcome. Each plugin lives in its own subdirectory — add a new one following the existing structure and include a `README.md`.

---

## License

All plugins in this repository are released under the [MIT License](./LICENSE).

---

*Built with [Claude Cowork](https://claude.ai) by Manoj Garg.*
