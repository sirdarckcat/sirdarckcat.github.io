N3 = {
"c_brainstorm": dict(group="lim", status="lean", impact="bound",
  title="Brainstorm: what a kernel could decide among 100 ideas",
  gist="On 2026-11-22 the research session sent 100 ideas for raising the record and asked the Lean session to try to prove each one wrong. Twenty-one of them contained a theorem; this file holds those, numbered as in the list.",
  detail="Examples. One exponent serves every row: N − q passes the base-2 Fermat test exactly when 2^(N−1) ≡ 2^q modulo it, so a scanner can reuse one exponent for all rows of N (fermat_common_exponent). No stopping rule helps: abandoning a candidate never spends fewer tests per success than never abandoning (never_abandon). Moves under the cap keep at most three new rows (move_keeps_at_most_three). For primes of 213,070 or more, a divisor shared by two rows is impossible (large_divisors_unique). The rest of the list is engineering, measurement or heuristic counting with no theorem in it.",
  note="Closes off many cheap-looking ideas with proofs, so the team does not spend campaigns on them. The standing record at the time was 133,981, then 6.3% of the modelled ceiling.",
  chips=["Cap/Brainstorm.lean", "24 theorems", "IDEAS100.md"]),
}
