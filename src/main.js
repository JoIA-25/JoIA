import {
  Viewer,
  DefaultViewerParams,
  SpeckleLoader,
  UrlHelper
} from "@speckle/viewer"
import { CameraController, SelectionExtension } from "@speckle/viewer"

async function main() {
  /** Get the HTML container */
  const container = document.getElementById("renderer")

  /** Configure the viewer params */
  const params = DefaultViewerParams
  params.showStats = false
  params.verbose = true

  /** Create Viewer instance */
  const viewer = new Viewer(container, params)
  /** Initialise the viewer */
  await viewer.init()

  /** Add the stock camera controller extension */
  viewer.createExtension(CameraController)
  /** Add the selection extension for extra interactivity */
  viewer.createExtension(SelectionExtension)

  /** Create a loader for the speckle stream */
  const urls = await UrlHelper.getResourceUrls(
    "https://app.speckle.systems/projects/4fe6b2ee63/models/6151567ec8"
  )
  for (const url of urls) {
    const loader = new SpeckleLoader(viewer.getWorldTree(), url, "")
    /** Load the speckle data */
    await viewer.loadObject(loader, true)
  }
}

main()
