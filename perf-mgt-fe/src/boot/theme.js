import { useThemeStore } from 'src/stores/theme'

export default ({ store }) => {
  const theme = useThemeStore(store)
  theme.initTheme()
}
