import { useConfigStore } from 'src/stores/config'

export default ({ store }) => {
  const config = useConfigStore(store)
  config.initTheme()
}