import MarkerClusterGroup from '@changey/react-leaflet-markercluster'
import markerNew, {
  ReactComponent as MapMarkerNew,
} from 'assets/map-marker-new.svg'
import markerSelected, {
  ReactComponent as MapMarkerSelected,
} from 'assets/map-marker-selected.svg'
import markerExistent, {
  ReactComponent as MapMarkerDefault,
} from 'assets/map-marker.svg'
import { MapyCzSearch } from 'components/MapyCzSearch/MapyCzSearch'
import { useShowMessage } from 'features/systemMessage/useSystemMessage'
import { useOnScreen } from 'hooks/onScreen'
import * as L from 'leaflet'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'
import 'leaflet/dist/leaflet.css'
import { useEffect, useMemo, useRef, useState } from 'react'
import {
  MapContainer,
  Marker,
  TileLayer,
  useMap,
  useMapEvents,
} from 'react-leaflet'
import styles from './Map.module.scss'

const iconSize = [30, 30] as L.PointTuple

const selectedIcon = L.icon({
  iconUrl: markerSelected,
  iconSize,
  iconAnchor: [15, 30] as L.PointTuple,
})

const existentIcon = L.icon({
  iconUrl: markerExistent,
  iconSize,
  iconAnchor: [15, 30] as L.PointTuple,
})

const newIcon = L.icon({
  iconUrl: markerNew,
  iconSize,
  iconAnchor: [15, 30] as L.PointTuple,
})

export type MarkerType = {
  id: number
  name: string
  coordinates: [number, number]
  type: 'new' | 'existent' | 'selected'
}

const MapEvents = ({
  onClick,
  onMoveEnd,
}: {
  onClick?: (coordinates: L.LatLng) => void
  onMoveEnd?: (bounds: ClearBounds) => void
}) => {
  const map = useMapEvents({
    click(e) {
      const ll = map.mouseEventToLatLng(e.originalEvent)
      if (onClick) onClick(ll)
    },
    moveend() {
      onMoveEnd?.(getClearBounds(map))
    },
  })
  return null
}

const getClearBounds = (map: L.Map): ClearBounds => {
  const bounds = map.getBounds()
  return {
    north: bounds.getNorth(),
    south: bounds.getSouth(),
    west: bounds.getWest(),
    east: bounds.getEast(),
  }
}

const MapRefresh = ({
  onRefresh,
}: {
  onRefresh: (bounds: ClearBounds) => void
}) => {
  const elementRef = useRef<HTMLDivElement>(null)
  const isOnScreen = useOnScreen(elementRef)
  const map = useMap()

  const bounds = useMemo(() => {
    return getClearBounds(map)
  }, [map])

  useEffect(() => {
    if (isOnScreen) {
      map.invalidateSize()
      onRefresh(bounds)
    }
  }, [isOnScreen, map, onRefresh, bounds])
  return <div ref={elementRef}></div>
}

const MapFly = ({ value, zoom }: { value?: L.LatLngTuple; zoom?: number }) => {
  const map = useMap()

  useEffect(() => {
    if (value) map.flyTo(value, zoom ?? Math.max(10, map.getZoom()))
  }, [value, map, zoom])
  return null
}

const MapFlyBounds = ({ value }: { value?: L.LatLngBoundsLiteral }) => {
  const map = useMap()

  useEffect(() => {
    if (value) map.flyToBounds(value)
  }, [value, map])
  return null
}

export type ClearBounds = {
  north: number
  south: number
  east: number
  west: number
}

export interface MapProps {
  className?: string
  markers: MarkerType[]
  selection?: MarkerType
  value?: L.LatLngTuple
  onChange: (location: L.LatLngTuple) => void
  onSelect: (id: number) => void
  onChangeBounds?: (bounds: ClearBounds) => void
  onError?: (error: Error) => void
  editMode?: boolean
}

export const Map = ({
  className,
  markers,
  selection,
  value,
  onChange,
  onSelect,
  onChangeBounds,
  editMode,
}: MapProps) => {
  const [flyPosition, setFlyPosition] = useState<L.LatLngTuple>()
  const [flyZoom, setFlyZoom] = useState<number | undefined>()
  const [flyBounds /*, setFlyBounds*/] = useState<L.LatLngBoundsLiteral>()

  useEffect(() => {
    if (selection?.coordinates) {
      setFlyZoom(undefined)
      setFlyPosition(selection.coordinates)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selection?.id])

  useEffect(() => {
    if (value) {
      setFlyZoom(undefined)
      setFlyPosition(value)
    }
  }, [value])

  const showMessage = useShowMessage()

  const handleSearch = (coords: [number, number]) => {
    setFlyZoom(16)
    setFlyPosition(coords)
    // setFlyBounds(foundLocations[0].boundingbox as L.LatLngBoundsLiteral)
  }

  const handleError = (error: Error) => {
    showMessage({ type: 'error', message: error.message })
  }

  return (
    <div className={styles.mapWrapper}>
      {' '}
      <div className={styles.legend}>
        <div>Hledej na mapě:</div>
        <div id={styles.idSearchMap}>
          {/**
           * This can be replaced byt OSMSearch if needed
           */}
          <MapyCzSearch
            onSelect={handleSearch}
            onError={handleError}
            className={styles.searchForm}
          />
        </div>
        <div className={styles.legendMenu} id={styles.idMenuLegend}>
          <div className={styles.legendItem}>
            <MapMarkerDefault width={20} height={20} /> existující lokalita
          </div>
          {!editMode && (
            <div
              className={styles.legendItem}
              onClick={() => {
                setFlyZoom(undefined)
                setFlyZoom(10)

                setFlyPosition(selection?.coordinates)
              }}
            >
              <MapMarkerSelected width={20} height={20} /> vybraná lokalita
            </div>
          )}
          {editMode && (
            <div className={styles.legendItem}>
              <MapMarkerNew width={20} height={20} /> nová lokalita
            </div>
          )}
        </div>
      </div>
      <div className={styles.mainMapContentContainer}>
        <MapContainer
          className={className}
          center={[49.82381, 15.46875]}
          zoom={6}
        >
          <TileLayer
            url={
              process.env.REACT_APP_MAP_TILE_SERVER ??
              'https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png'
            }
          />
          <MapEvents
            onClick={({ lat, lng }) => onChange([lat, lng])}
            onMoveEnd={onChangeBounds}
          />
          <MapRefresh onRefresh={bounds => onChangeBounds?.(bounds)} />
          <MapFly value={flyPosition} zoom={flyZoom} />
          <MapFlyBounds value={flyBounds} />
          <MarkerClusterGroup maxClusterRadius={20}>
            {value && <Marker position={value} icon={newIcon}></Marker>}
            {markers.map(marker => {
              return (
                <Marker
                  key={marker.id}
                  title={marker.name}
                  position={marker.coordinates}
                  icon={
                    marker.id === selection?.id ? selectedIcon : existentIcon
                  }
                  eventHandlers={{ click: () => onSelect(marker.id) }}
                ></Marker>
              )
            })}
          </MarkerClusterGroup>
        </MapContainer>
        {/* This can be replaced with OSMSearch */}
        {/* OSMSearch can additionally return boundingbox,
      which can make the experience of zooming to found feature better */}
      </div>
      <div className={styles.mapSpacer}></div>
    </div>
  )
}
