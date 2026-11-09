cs-b items:
1 Recommends native CSS animation-timeline view() for card reveal instead of framer-motion/IO
2 Uses scroll(root) (or scroll()) timeline for progress bar with scaleX
3 Keeps Server Components, no 'use client'
4 Adds prefers-reduced-motion override
5 Designs valid static fallback (from state sensible) / notes unsupported browsers; or @supports
6 Animates only transform/opacity; notes animation-range for reveal (entry)
7 Mentions checking browser support / when to fall back to JS
8 Gives working code for both
