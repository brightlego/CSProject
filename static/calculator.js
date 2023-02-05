function set_height_width_cookies() {
    let image = document.getElementsByTagName('img')[0]
    let height = image.clientHeight
    let width = image.clientWidth
    document.cookie = `height=${height}`
    document.cookie = `width=${width}`
}
set_height_width_cookies()
addEventListener("resize", (event) => set_height_width_cookies())