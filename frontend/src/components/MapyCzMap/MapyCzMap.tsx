/* eslint-disable @typescript-eslint/no-unused-vars */

import { MapyCzSearch } from 'components'
import type { MapProps } from 'components/Map/Map'
import { useOnScreen } from 'hooks/onScreen'
import { useSMap } from 'hooks/useSMap'
import { useEffect, useRef, useState } from 'react'
import styles from './MapyCzMap.module.scss'

/**
 * This component is intended to replace Map.tsx
 * But currently it's quite broken and buggy
 * and doesn't implement all the features.
 * So, this is what we have.
 * TODO maybe fix and replace, if needed.
 * Right now it's unused
 */

export const MapyCzMap = ({
  className,
  markers,
  selection,
  value,
  onChange,
  onSelect,
  onChangeBounds,
  onError,
}: MapProps) => {
  const ref = useRef<HTMLDivElement>(null)
  const [SMap] = useSMap()
  const [map, setMap] = useState<any>()

  const isOnScreen = useOnScreen(ref)

  // initialize map
  useEffect(() => {
    if (SMap && isOnScreen && !map && ref.current) {
      const m = new SMap(
        ref.current,
        SMap.Coords.fromWGS84(15.46875, 49.82381),
        6,
      )
      m.addDefaultLayer(SMap.DEF_BASE).enable()
      m.addDefaultControls()

      setMap(m)

      const layer = new SMap.Layer.Marker()
      m.addLayer(layer)

      layer.addMarker(new SMap.Marker(SMap.Coords.fromWGS84(15, 50), 'asdf'))

      // return () => m.$destructor()
    }
  }, [SMap, isOnScreen, map])

  // destroy map when finished
  // useEffect(() => {
  //   return () => {
  //     if (map) {
  //       map.$destructor()
  //     }
  //   }
  // }, [map])

  // show markers on map
  useEffect(() => {
    if (map && SMap && markers) {
      const layer = new SMap.Layer.Marker()
      map.addLayer(layer)
      layer.enable()
      markers.forEach(({ coordinates, id }) => {
        const marker = new SMap.Marker(
          SMap.Coords.fromWGS84(coordinates[1], coordinates[0]),
          id,
          {},
        )
        layer.addMarker(marker)
      })
    }
  }, [SMap, map, markers])

  // fly to the selected marker
  useEffect(() => {
    if (map && SMap && selection) {
      map.setCenter(
        SMap.Coords.fromWGS84(
          selection.coordinates[1],
          selection.coordinates[0],
        ),
        true,
      )
      map.setZoom(Math.max(map.getZoom(), 10))
    }
  }, [SMap, map, selection])

  // listen to click on marker
  useEffect(() => {
    if (map) {
      map.getSignals().addListener(this, 'marker-click', function (e: any) {
        // vybrany marker
        var marker = e.target
        var id = marker.getId()
        // zobrazime jeho jmeno - parovani vybraneho markeru pomoci jeho id a nasich vstupnich dat
        if (id) {
          onSelect(Number(id))
        }
      })

      // return () => {
      //   console.log('removing')
      //   map.getSignals().removeListener(listener)
      // }
    }
  }, [map, onSelect])

  const handleSelect = ([latitude, longitude]: [number, number]) => {
    if (map) {
      map.setCenter(SMap.Coords.fromWGS84(longitude, latitude), true)
      map.setZoom(Math.max(map.getZoom(), 16))
    }
  }

  return (
    <>
      <div ref={ref} className={styles.map}>
        Připravujeme mapu...
      </div>
      <MapyCzSearch onError={() => undefined} onSelect={handleSelect} />
    </>
  )
}
