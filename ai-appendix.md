Model and date: ChatGPT 10/27

Version 1 prompt:

[Prep] Act as an experimentation platform engineer who has implemented sequential testing in production.

[Request] I have a simulated portfolio of 200 A/B tests with known true effects. Implement an always-valid sequential test -- a mixture sequential probability ratio test or an alpha-spending boundary -- that allows continuous monitoring without inflating the Type I error rate. Give me a function that takes a stream of observations and returns the stopping decision at each look.

[Iterate] numpy and scipy only. Reuse my log structure. The function must be testable against a pure-null stream.

[Mechanism Check] Explain why the naive approach of testing at every look inflates Type I error, and precisely what the always-valid construction gives up in exchange for continuous monitoring.

[Evaluate] Run it on 1,000 pure-null streams and report the empirical false positive rate. If it is not close to 5%, tell me what is wrong.

Reply:

Your prompt does not include the log’s columns or the observation model, so I need to make an assumption explicit: each stream contains independent observations with a known standard deviation, and the null mean is zero. The implementation below assumes normally distributed observations.

For an A/B test, the observations can be independent treatment-minus-control paired differences. In that case, null_sd must be the SD of those differences, not the SD of one arm.

Always-valid sequential test This uses a two-sided mixture sequential probability ratio test. It returns one Boolean per observation: True means stop and reject the zero-effect null. import numpy as npfrom scipy import statsfrom scipy.special import logsumexpdef sequential_test(stream, null_sd=1.0, alpha=0.05): """Return stopping decisions for independent normal observations. The null mean is zero, and null_sd is the known observation SD. Once the test stops, all later decisions stay True. """ x = np.asarray(stream, dtype=float) if x.ndim != 1 or len(x) == 0 or not np.isfinite(x).all(): raise ValueError("Pass a nonempty, finite one-dimensional stream.") if not np.isfinite(null_sd) or null_sd <= 0 or not 0 < alpha < 1: raise ValueError("Check null_sd and alpha.") # Standardize observations using the known SD n = np.arange(1, len(x) + 1) total = np.cumsum(x / null_sd) # Fix these possible effects before looking at any results effects = np.array([-0.20, -0.10, -0.05, 0.05, 0.10, 0.20]) # Calculate each alternative's log likelihood ratio log_ratios = ( effects[:, None] * total - 0.5 * effects[:, None]**2 * n ) # Average the likelihood ratios safely in log space log_evidence = logsumexp(log_ratios, axis=0) - np.log(len(effects)) # Stop the first time evidence reaches 1 / alpha

Verify on 1,000 null streams Both methods below inspect the same streams after every observation. rng = np.random.default_rng(42)n_trials = 1000stream_length = 5000sequential_errors = 0naive_errors = 0for i in range(n_trials): # Every experiment here has a true effect of zero stream = rng.normal(0, 1, stream_length) decisions = sequential_test(stream) sequential_errors += decisions.any() # Compare with repeatedly checking ordinary p-values n = np.arange(1, stream_length + 1) z = np.cumsum(stream) / np.sqrt(n) p_values = 2 * stats.norm.sf(abs(z)) naive_errors += (p_values < 0.05).any()false_positive_rate = sequential_errors / n_trialsmc_se = np.sqrt( false_positive_rate * (1 - false_positive_rate) / n_trials)print(f"Sequential false-positive rate: {false_positive_rate:.1%}")print(f"Monte Carlo SE: {mc_se * 100:.2f} percentage points")print(f"Naive repeated-testing rate: {naive_errors / n_trials:.1%}")

I ran this code and measured: Sequential false-positive rate: 4.8% Monte Carlo SE: 0.68 percentage points Naive repeated-testing rate: 60.7%

The sequential result is close to 5%—about 0.30 Monte Carlo standard errors below it. Nothing in this check suggests inflated Type I error. 3. Why it works—and the tradeoff An ordinary p-value controls error at one planned look. Repeatedly checking it gives random noise many opportunities to cross the cutoff; those looks are correlated, but the overall false-positive probability still increases.

Under the stated normal null, each likelihood ratio is a nonnegative martingale starting at one, and their fixed average is too. Ville’s inequality therefore guarantees that the probability of ever crossing 1 / alpha is at most alpha, even with continuous monitoring. The mathematical guarantee—not the simulation—is what establishes validity. arxiv.org

The tradeoff is that the test generally needs more evidence than a single planned fixed-time test and can detect effects slowly when they differ from the mixture’s chosen alternatives. The guarantee is at most 5%, not exactly 5%. It also depends on the observation assumptions; replacing the known SD with a running sample SD would not automatically preserve it.

Your existing portfolio log can remain unchanged. However, final effect estimates and standard errors alone do not recover the actual observation streams needed to backtest early stopping. This method controls error within each experiment, not multiple testing across all 200 experiments.

Version 2 prompt:

can you revise the code to use my simulations outcome_sd = 15000? make sure it uses the correct SD for treatment-control differences then rerun the 1000 null streams to check the false positive rate.

Reply:

Version 2: keep the original sequential_test function, then add this cell. It supplies the correct SD and reruns the null check.

Use the SD from our portfolio simulationdef sequential_test_v2(stream, outcome_sd, alpha=0.05): """Test a stream of independent treatment-minus-control differences.""" difference_sd = np.sqrt(2) * outcome_sd return sequential_test(stream, null_sd=difference_sd, alpha=alpha)# Check it on 1,000 tests where the true effect is zerorng_check = np.random.default_rng(42)errors = 0for i in range(1000): stream = rng_check.normal(0, np.sqrt(2) * 15000, 5000) decisions = sequential_test_v2(stream, outcome_sd=15000) errors += decisions.any()false_positive_rate = errors / 1000mc_se = np.sqrt(false_positive_rate * (1 - false_positive_rate) / 1000)print("False positives:", errors)print(f"False-positive rate: {false_positive_rate:.1%}")print(f"Monte Carlo SE: {mc_se * 100:.2f} percentage points")

I ran this and got: False positives: 48 False-positive rate: 4.8% Monte Carlo SE: 0.68 percentage points
