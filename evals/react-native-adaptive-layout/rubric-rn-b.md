rn-b items:
1 Warns iPad landscape/all orientations may be reachable despite orientation:portrait; check generated Info.plist
2 Warns Android API 36 ignores screenOrientation lock on >=600dp (large screens)
3 Names the fold/breakpoint remount risk destroying in-progress form input; requires state preservation proven by test
4 Proposes keeping ONE navigator and switching bar vs rail via style (not swapping components/remounting)
5 Mentions tabletop posture exception (rail vs bar when half-folded) / width-only is incomplete
6 Notes expo-router native tabs do not adapt on Android (need custom rail); iPad sidebarAdaptable
7 Mentions measuring content area not window when a rail is present, or safe-area left inset with iPad sidebar
8 Decides by width (window size classes ~600dp), not device type
