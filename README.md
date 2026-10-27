[README.md](https://github.com/user-attachments/files/34051291/README.md)
# Auditing an Experiment Portfolio — Power, Selection & Sequential Testing

## Objective

I audited a simulated experiment programme to see whether reported wins translated into real revenue.

## Methodology

- Simulated 200 experiments with known true effects and different sample sizes.
- Applied the client's p < 0.05 shipping rule and compared estimated effects with truth.
- Examined the winner's curse across low-, medium- and high-power groups.
- Wrote a bootstrap loop, checked it against SciPy and calculated a BCa interval.
- Compared a stricter shipping rule on the same portfolio.
- Created `src/experiment_portfolio.py` with reusable functions and assertions.
- Revised an AI-generated sequential test, checked 1,000 null streams and recorded the exchange in [ai-appendix.md](ai-appendix.md).
- Wrote a CFO memo with numbers traced to the notebook's final cell.

## Key Findings

The client shipped **31 experiments**, of which **32.3% had no true effect**. Average estimated gains were **$772.51**, compared with true gains of **$758.51**.

The stricter rule reduced false ships to **7.1%**, but true revenue fell from **$23,513.73 to $15,136.71** because it also rejected genuine gains.

The sequential test had a **4.8%** false-positive rate, with Monte Carlo SE **0.68 percentage points**, compared with **60.7%** for naive repeated testing.

