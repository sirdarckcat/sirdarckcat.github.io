# literature_novelty — working notes (referee, 25 Nov 2026)

Sources actually read (PDF text extracted locally into consultcheck/dl/):
- Granville, van de Lune, te Riele 1989, CWI report NM-R8812 https://ir.cwi.nl/pub/5933/5933D.pdf
  p.11: "On probabilistic grounds we conjecture that for n>10, p(n) << log^2 n loglog n. From Table 3 we derive that
  p(n)/(log^2 n loglog n) < 1.603 for all n <= 2*10^10." Upper-bound conjecture, no constant conjectured, no lower bound.
  Verified to 2*10^10, max p(n)=2029 there. Conditional (H-L k-tuples) theorem on #{n<=N: p(n)<=Q}.
- W. Shi, arXiv:2605.21529 v6 (19 May 2026, rev 22 Sep 2026), Thm 6.22:
  (i) #{n<=X even: p(n)<=z} <= pi(z) X/log X (1+o(1)), 2<=z<=X^(1/2); (ii) p(n) > psi(n) log n loglog n for almost all even n;
  (iii) max_{n<=X even} p(n) >= (1/2+o(1)) log X loglog X.  "we have not found these lower bounds stated in the literature."
  Remark 6.24: "1/2 log X log log X is the limit of pure counting ... an improvement would need a covering construction in the
  spirit of FGKMT, here covering only the primes p <= z rather than a whole interval."  => the team's results answer this remark.
- Oliveira e Silva page https://sweet.ua.pt/tos/goldbach.html : 4*10^18 reached 4 Apr 2012; double-check to 4*10^17;
  record p=9781 at 3325581707333960528 (S. Pardi, 16 Jan 2012); GvdLtR quoted; fit p ~ 0.33 (log S loglog S)^2.
  My arithmetic: 9781/(ln^2 n lnln n)=1.433 ; 9781/(ln n lnln n)=61.1.
- FGKMT arXiv:1412.5029 (JAMS 31 (2018) 65-105): G(X) >> log X log2 X log4 X / log3 X.
- FGKT arXiv:1408.4505 (Annals 183 (2016)): G(X) >= f(X) log X log2 X log4 X/(log3 X)^2, f -> infinity. Maynard arXiv:1408.5110 same.
- FKMPT "Long gaps in sieved sets" arXiv:1802.07604 (JEMS 23 (2021)).
- Ziller/Morack-type "paired Jacobsthal": arXiv:1706.00317.
- Gridbach (self-reported, Medium 2025): 4*10^18 + 7*10^13; not peer reviewed.

Team items checked:
- research README l.756-764 cites GvdLtR and Shi correctly (Shi statement exact). "conjectured maximal order" slightly overstates:
  GvdLtR is a << conjecture.
- consultant ledger_thesis.md lower_bound_thm: "g(N) >> (log N)(log_2 N)(log_4 N)/log_3 N ... this equals the best known
  prime-gap order" and sandwich_open "the question is whether covering only the prime offsets ... asymptotically beats the
  prime-gap scale": the FGKMT-interval bound is SMALLER than Shi's counting bound (log4/log3 -> 0), and the question is
  answered yes by counting alone. Stale entries.
- COHERENT_BLOCK.md theorem Q = c x ln^2 x ln3 x/(ln2 x)^2: read the proof; steps are sound as far as I can see; it is the
  Erdos-Rankin smooth-number device on shifted primes with an average over the common integer N1. Order beats ln N ln2 N by
  ln2 N ln4 N/(ln3 N)^2 -> infinity.
Novelty: nothing found in literature above (1/2) ln X ln ln X. Both team statements look new; neither is deep.
