export const SHEET_STOPS = ["collapsed", "half", "full"]

export const sheetHeights = (containerHeight, collapsedHeight) => ({
  collapsed: collapsedHeight,
  half: Math.round(containerHeight * 0.55),
  full: Math.round(containerHeight * 0.92),
})

export const nearestStop = (heights, height) =>
  SHEET_STOPS.reduce((best, stop) =>
    Math.abs(heights[stop] - height) < Math.abs(heights[best] - height) ? stop : best,
  )

export const clampHeight = (heights, height) =>
  Math.min(heights.full, Math.max(heights.collapsed, height))

export const nextStopOnTap = stop => (stop === "collapsed" ? "half" : "collapsed")
