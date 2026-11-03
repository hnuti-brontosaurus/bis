const PHOTO_MAX_SIDE = 2000
const PHOTO_QUALITY = 0.85

// The API's Base64 image field wants the file's name in the header.
const withFilename = (dataUri, file) =>
  dataUri.replace(
    ";base64,",
    `;filename=${encodeURIComponent(file.name.replace(/\.[^.]*$/, "")) || "photo"};base64,`,
  )

const readAsDataUri = blob =>
  new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result)
    reader.onerror = () => reject(reader.error)
    reader.readAsDataURL(blob)
  })

/**
 * A phone photo as a JPEG data URI no bigger than PHOTO_MAX_SIDE, since it is
 * kept on the phone until there is signal and sent as base64.
 */
export const photoDataUri = async file => {
  const bitmap = await createImageBitmap(file)
  const scale = Math.min(1, PHOTO_MAX_SIDE / Math.max(bitmap.width, bitmap.height))
  const canvas = document.createElement("canvas")
  canvas.width = Math.round(bitmap.width * scale)
  canvas.height = Math.round(bitmap.height * scale)
  canvas.getContext("2d").drawImage(bitmap, 0, 0, canvas.width, canvas.height)
  bitmap.close()
  return withFilename(canvas.toDataURL("image/jpeg", PHOTO_QUALITY), file)
}

export const fileDataUri = async file => withFilename(await readAsDataUri(file), file)
