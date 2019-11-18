# Tohle je správná funkce "tah", ale nebereme ji jako vlastní řešení úkolu :)
tah = lambda p, n, s: ''.join(s if i==n else c for i, c in enumerate(p)) if p[n:n+1] == '-' else int('')

