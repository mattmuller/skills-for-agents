cs-a items:
1 Identifies overflow:hidden creating scroll container freezing view() timeline; use overflow:clip
2 Identifies top-of-page hero needs animation-range entry 100% exit 100% (entry already happened)
3 Extends bg wrapper beyond container (negative inset >= translation) so translate does not expose gaps
4 Adds prefers-reduced-motion override disabling the animation
5 Notes static fallback / unsupported browsers stay at from keyframe
6 Animates wrapper/ keeps only transform/opacity
7 Checks/mentions browser support
