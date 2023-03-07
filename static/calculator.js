function set_height_width_cookies() {
    let image = document.getElementsByTagName('img')[0]
    let height = image.clientHeight
    let width = image.clientWidth
    document.cookie = `height=${height}`
    document.cookie = `width=${width}`
}
set_height_width_cookies()
addEventListener("resize", (event) => set_height_width_cookies())

function save_graph() {
    let text = document.getElementsByName("raw_text")[0].value
    document.getElementsByName("content")[0].value = text
}

function graph() {
    let filename = document.getElementsByName("filename")[0].value
    let description = document.getElementsByName("description")[0].value
    document.getElementsByName("filename2")[0].value = filename
    document.getElementsByName("description2")[0].value = description
}