import { yupResolver } from '@hookform/resolvers/yup'
import { skipToken } from '@reduxjs/toolkit/dist/query'
import { api } from 'app/services/bis'
import type { Location } from 'app/services/bisTypes'
import classNames from 'classnames'
import {
  Button,
  ClearBounds,
  FormInputError,
  FormInputErrorSimple,
  InfoBox,
  InlineSection,
  Label,
  MarkerType,
  SelectObject,
} from 'components'
import { toDecimal } from 'geolib'
import { LatLngTuple } from 'leaflet'
import { cloneDeep } from 'lodash'
import merge from 'lodash/merge'
import React, {
  forwardRef,
  Suspense,
  useEffect,
  useMemo,
  useState,
} from 'react'
import { FormProvider, useForm, UseFormReturn } from 'react-hook-form'
import { AiOutlineEdit } from 'react-icons/ai'
import { FiCheckCircle } from 'react-icons/fi'
import { TbMap2 } from 'react-icons/tb'
import { Overwrite } from 'utility-types'
import { required } from 'utils/validationMessages'
import * as yup from 'yup'
import styles from './SelectLocation.module.scss'

const Map = React.lazy(async () => {
  const { Map } = await import('components/Map')
  return { default: Map }
})

export type NewLocation = Overwrite<
  Pick<Location, 'gps_location' | 'name' | 'address' | 'description'>,
  { gps_location?: Omit<Required<Location>['gps_location'], 'type'> }
>

const newLocationSchema: yup.ObjectSchema<NewLocation> = yup.object({
  name: yup.string().trim().required(),
  gps_location: yup
    .object({
      coordinates: yup
        .tuple([
          yup
            .number()
            .required()
            .min(-180)
            .max(180)
            .test(
              'coordinate',
              'Zadejte platnou GPS souřadnici',
              value => typeof toDecimal(value) === 'number',
            ),
          yup
            .number()
            .required()
            .min(-90)
            .max(90)
            .test(
              'coordinate',
              'Zadejte platnou GPS souřadnici',
              value => typeof toDecimal(value) === 'number',
            ),
        ])
        .required(),
    })
    .required(),
  address: yup.string(),
  description: yup.string(),
})

export type SelectedOrNewLocation = NewLocation | Location

// This is the main component that renders the map and the form for creating new locations
export const SelectLocation = forwardRef<
  any,
  {
    errorMessage?: string
    value: SelectedOrNewLocation | null
    onChange: (location: SelectedOrNewLocation | null) => void
    colorTheme?: string
  }
>(({ value, onChange, errorMessage, colorTheme }, ref) => {
  const [isEditing, setIsEditing] = useState(false)
  const [bounds, setBounds] = useState<ClearBounds>()

  const { data: locations, isLoading } = api.endpoints.readLocations.useQuery(
    bounds ? { pageSize: 5000 } : skipToken,
  )

  const newLocationMethods = useForm<NewLocation>({
    resolver: yupResolver(newLocationSchema),
  })

  const locationsWithGPS = useMemo(
    () =>
      (locations?.results ?? []).filter(
        location => location?.gps_location?.coordinates,
      ),
    [locations],
  )
  const selectedLocation = value

  // here we hold the coordinates of new location in map
  const [newLocationCoordinates, setNewLocationCoordinates] = useState<
    LatLngTuple | undefined
  >()

  useEffect(() => {
    if (!newLocationCoordinates)
      newLocationMethods.setValue('gps_location', undefined)
    else {
      newLocationMethods.setValue(
        'gps_location.coordinates.0',
        newLocationCoordinates[1],
      )
      newLocationMethods.setValue(
        'gps_location.coordinates.1',
        newLocationCoordinates[0],
      )
      newLocationMethods.trigger('gps_location')
    }
  }, [newLocationCoordinates, newLocationMethods])

  const markers: MarkerType[] = useMemo(() => {
    const markers: MarkerType[] = locationsWithGPS.map(location => ({
      type: 'existent',
      id: location.id,
      name: location.name,
      // api has coordinates switched, so we switch them, and we'll have to switch back when saving
      coordinates: [
        ...(location.gps_location?.coordinates as [number, number]),
      ].reverse() as LatLngTuple,
    }))

    if (value && 'id' in value) {
      // api has coordinates switched, so we switch them, and we'll have to switch back when saving
      const selectedMarker = markers.find(
        marker => Number(marker.id) === Number(value.id),
      )

      if (selectedMarker) {
        selectedMarker.type = 'selected'
      } else if (selectedLocation?.gps_location?.coordinates) {
        const [lng, lat] = selectedLocation.gps_location.coordinates
        const coordinates = [lat, lng] as LatLngTuple

        markers.push({
          type: 'selected',
          name: selectedLocation.name,
          coordinates,
          id: 'id' in selectedLocation ? selectedLocation.id : 0,
        })
      }
    } else if (!isEditing && value?.name && value?.gps_location?.coordinates) {
      markers.push({
        type: 'selected',
        name: value.name,
        coordinates: [
          value.gps_location.coordinates[1],
          value.gps_location.coordinates[0],
        ],
        id: -1,
      })
    }

    return markers
  }, [locationsWithGPS, value, selectedLocation, isEditing])

  const selection = useMemo(
    () => markers.find(marker => marker.type === 'selected'),
    [markers],
  )

  const handleSelect = (id: number) => {
    setIsEditing(false)
    onChange(
      locations!.results.find(location => location.id === id) as Location,
    )
  }

  // do this when CreateLocation is finished
  const handleFinish = (location?: NewLocation) => {
    setIsEditing(false)
    if (location) onChange(location)
  }

  return (
    <div
      className={classNames(
        styles.wrapper,
        colorTheme === 'opportunities' && styles.opportunitiesLocation,
      )}
    >
      <div className={styles.topContentContainer}>
        <div className={styles.selectLocationBox}>
          {isEditing ? (
            <div className={styles.editingLocation}>
              <h3>Přidávání nového místa konání</h3>
              <AiOutlineEdit size={36} className={styles.editStatePending} />
            </div>
          ) : (
            <div className={styles.selectLocationItem}>
              <span>Vyber místo konání podle názvu</span>
              <FormInputErrorSimple
                className={styles.selectLocationErrorWrapper}
                errorMessage={errorMessage}
                isBlock
              >
                <div className={styles.selectLocationWithIcon}>
                  <SelectObject<Location>
                    className={classNames(
                      styles.aboveMap,
                      styles.fullWidth,
                      styles.selectLocation,
                    )}
                    value={(value as Location) ?? undefined}
                    onChange={onChange}
                    getLabel={location => location.name}
                    getValue={location => String(location.id)}
                    placeholder="Název"
                    search={api.endpoints.readLocations}
                    ref={ref}
                    colorTheme={colorTheme}
                  />
                  {value ? (
                    <FiCheckCircle size={36} className={styles.editStateDone} />
                  ) : (
                    <AiOutlineEdit
                      size={36}
                      className={styles.editStatePending}
                    />
                  )}
                </div>
              </FormInputErrorSimple>
            </div>
          )}
        </div>
        {isEditing ? (
          <Button
            secondary
            onClick={() => {
              setIsEditing(false)
            }}
            className={classNames(
              styles.buttonBigScreen,
              styles.buttonNewLocalization,
            )}
          >
            Vyber existující místo konání
          </Button>
        ) : (
          <Button
            secondary
            onClick={() => {
              setIsEditing(true)
              onChange(null)
            }}
            className={classNames(
              styles.buttonBigScreen,
              styles.buttonNewLocalization,
            )}
          >
            Přidat nové místo konání
          </Button>
        )}
      </div>
      <div className={styles.mainContentContainerWrapper}>
        <div className={styles.mainContentContainer}>
          <div className={styles.mapColumn}>
            <Suspense
              fallback={
                <div
                  className={classNames(
                    styles.mapContainer,
                    'leaflet-container',
                  )}
                />
              }
            >
              <Map
                // This classname is used by the "useSwipe" hook to ignore swipe events on this element.
                // If removed, the main step swipe will also happen on map swipe, which is not desired behavior.
                // Be careful when editing this classname, as it may affect the swipe functionality.
                className={classNames(
                  styles.mapContainer,
                  'steps-change-swipe-ignored',
                )}
                markers={markers}
                selection={selection}
                value={isEditing ? newLocationCoordinates : undefined}
                onChange={coordinates => {
                  if (isEditing) {
                    setNewLocationCoordinates(coordinates)
                  }
                }}
                onSelect={handleSelect}
                onChangeBounds={bounds => setBounds(bounds)}
                editMode={isEditing}
              />
            </Suspense>
          </div>
          <div className={styles.mapSpacer}></div>
          {isEditing ? (
            <CreateLocation
              methods={newLocationMethods}
              onChangeCoordinates={coords => setNewLocationCoordinates(coords)}
              onFinish={handleFinish}
            />
          ) : (
            <ViewLocation
              isLoading={isLoading}
              location={selectedLocation ?? undefined}
            />
          )}
          {isEditing ? (
            <Button
              secondary
              onClick={() => {
                setIsEditing(false)
              }}
              className={classNames(
                styles.buttonSmallScreen,
                styles.buttonNewLocalization,
              )}
            >
              Vyber existující místo konání
            </Button>
          ) : (
            <Button
              secondary
              onClick={() => {
                setIsEditing(true)
              }}
              className={classNames(
                styles.buttonSmallScreen,
                styles.buttonNewLocalization,
              )}
            >
              Přidat nové místo konání
            </Button>
          )}
        </div>
      </div>
    </div>
  )
})

const CreateLocation = ({
  formId = 'create-location',
  methods,
  onChangeCoordinates,
  onFinish,
}: {
  formId?: string
  methods: UseFormReturn<NewLocation>
  onChangeCoordinates: (coords: LatLngTuple | undefined) => void
  onFinish: (location?: NewLocation) => void
}) => {
  const { onBlur: blurLatitude, ...registerLatitude } = methods.register(
    'gps_location.coordinates.1',
    { required },
  )
  const { onBlur: blurLongitude, ...registerLongitude } = methods.register(
    'gps_location.coordinates.0',
    { required },
  )

  /**
   * When both latitude and longitude are set, we parse the values
   * and when they're ok, we do stuff (e.g. fly to that place)
   */
  const handleGPSBlur = () => {
    const rawCoordinates = methods.getValues('gps_location.coordinates')

    const parsedCoords: [unknown, unknown] = toDecimal(rawCoordinates)

    const areCoordinatesNumeric = parsedCoords.every(
      coord => typeof coord === 'number',
    )

    if (areCoordinatesNumeric) {
      const coordinates = parsedCoords.reverse() as LatLngTuple
      onChangeCoordinates(coordinates)
    } else {
      onChangeCoordinates(undefined)
    }
  }

  const handleConfirm = methods.handleSubmit(data => onFinish(cloneDeep(data)))

  const handleCancel = () => {
    methods.reset({})
    onFinish()
  }

  return (
    <div className={classNames(styles.locationInfo)}>
      <FormProvider {...methods}>
        <InlineSection>
          <Label htmlFor="location.name" required>
            Název:
          </Label>
          <FormInputError>
            <input
              id="location.name"
              type="text"
              form={formId}
              {...methods.register('name', { required })}
            />
          </FormInputError>
        </InlineSection>
        <InfoBox>Vyber bod na mapě nebo vpiš GPS souřadnice.</InfoBox>
        <InlineSection>
          <Label htmlFor="location.gps" required>
            GPS:
          </Label>
        </InlineSection>
        <InlineSection>
          <FormInputError>
            <input
              type="text"
              id="location.gps"
              placeholder="50.01234567"
              form={formId}
              {...registerLatitude}
              onBlur={e => {
                handleGPSBlur()
                blurLatitude(e)
              }}
            />
          </FormInputError>
          N
        </InlineSection>
        <InlineSection>
          <FormInputError>
            <input
              type="text"
              placeholder="14.98765432"
              form={formId}
              {...registerLongitude}
              onBlur={e => {
                handleGPSBlur()
                blurLongitude(e)
              }}
            />
          </FormInputError>
          E
        </InlineSection>
        <InlineSection>
          <Label htmlFor="location.address">Adresa:</Label>{' '}
          <FormInputError>
            <input
              type="text"
              id="location.address"
              form={formId}
              {...methods.register('address')}
            />
          </FormInputError>
        </InlineSection>
        <InlineSection>
          <Label htmlFor="location.description">Popis:</Label>
          <FormInputError>
            <textarea
              id="location.description"
              form={formId}
              {...methods.register('description')}
            />
          </FormInputError>
        </InlineSection>
        <div className={styles.saveLocationButtons}>
          <Button
            secondary
            small
            type="reset"
            form={formId}
            onClick={handleCancel}
          >
            Zrušit
          </Button>
          <Button
            primary
            small
            type="submit"
            form={formId}
            onClick={handleConfirm}
          >
            Potvrdit místo konání
          </Button>
        </div>
      </FormProvider>
    </div>
  )
}
const ViewLocation = ({
  location,
  isLoading,
}: {
  location?: NewLocation | Location
  isLoading: boolean
}) => {
  return (
    <div
      className={classNames(
        styles.locationInfo,
        location && styles.locationSelected,
      )}
    >
      {location && location.name ? (
        <>
          <div className={styles.fieldTitle}>{location?.name}</div>

          <div className={styles.fieldText}>{location?.address}</div>
          <div className={styles.fieldText}> {location?.description}</div>
        </>
      ) : isLoading ? (
        <div className={styles.emptyLocation}>
          <div>Načítáme lokality</div>
        </div>
      ) : (
        <div className={styles.emptyLocation}>
          {/* <SelectMap width={150} height={100} /> */}
          <TbMap2 strokeWidth={1} />
          <div>Vyber místo konání podle názvu nebo na mapě</div>
        </div>
      )}
    </div>
  )
}

export const useCreateOrSelectLocation = () => {
  const [createLocation] = api.endpoints.createLocation.useMutation()

  const createOrSelectLocation = async (
    location: NewLocation | Pick<Location, 'id'>,
  ) => {
    if (!location) {
      return null
    } else if ('id' in location) {
      return location.id
    } else {
      // create new location
      const newLocation = await createLocation(
        merge({}, location, {
          patron: null,
          contact_person: null,
          gps_location: {
            type: 'Point',
          },
        }) as unknown as Omit<Location, 'id'>,
      ).unwrap()
      return newLocation.id
    }
  }

  return createOrSelectLocation
}
