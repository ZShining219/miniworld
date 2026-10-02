"""Tiny local gazetteer for public job-location strings.

Coordinates are city-level centroids shipped inside the repository. This module
performs no network access: job location text is matched locally and resolved
to a city centroid, never to a home address. Anything that does not match stays
unresolved instead of being fabricated.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class GazetteerPlace:
    name: str
    latitude: float
    longitude: float
    aliases: tuple[str, ...]


_GAZETTEER: tuple[GazetteerPlace, ...] = (
    # Mainland China
    GazetteerPlace("上海", 31.2304, 121.4737, ("shanghai", "上海")),
    GazetteerPlace("北京", 39.9042, 116.4074, ("beijing", "北京", "peking")),
    GazetteerPlace("深圳", 22.5431, 114.0579, ("shenzhen", "深圳")),
    GazetteerPlace("广州", 23.1291, 113.2644, ("guangzhou", "广州", "canton")),
    GazetteerPlace("杭州", 30.2741, 120.1551, ("hangzhou", "杭州")),
    GazetteerPlace("成都", 30.5728, 104.0668, ("chengdu", "成都")),
    GazetteerPlace("南京", 32.0603, 118.7969, ("nanjing", "南京")),
    GazetteerPlace("苏州", 31.2989, 120.5853, ("suzhou", "苏州")),
    GazetteerPlace("武汉", 30.5928, 114.3055, ("wuhan", "武汉")),
    GazetteerPlace("西安", 34.3416, 108.9398, ("xi'an", "xian", "西安")),
    GazetteerPlace("重庆", 29.5630, 106.5516, ("chongqing", "重庆")),
    GazetteerPlace("合肥", 31.8206, 117.2272, ("hefei", "合肥")),
    GazetteerPlace("长沙", 28.2282, 112.9388, ("changsha", "长沙")),
    GazetteerPlace("天津", 39.0842, 117.2010, ("tianjin", "天津")),
    GazetteerPlace("珠海", 22.2710, 113.5767, ("zhuhai", "珠海")),
    GazetteerPlace("厦门", 24.4798, 118.0894, ("xiamen", "厦门")),
    GazetteerPlace("大连", 38.9140, 121.6147, ("dalian", "大连")),
    GazetteerPlace("青岛", 36.0671, 120.3826, ("qingdao", "青岛")),
    # Greater China / East Asia
    GazetteerPlace("香港", 22.3193, 114.1694, ("hong kong", "hongkong", "hk", "香港")),
    GazetteerPlace("台北", 25.0330, 121.5654, ("taipei", "台北")),
    GazetteerPlace("东京", 35.6762, 139.6503, ("tokyo", "東京", "东京")),
    GazetteerPlace("大阪", 34.6937, 135.5023, ("osaka", "大阪")),
    GazetteerPlace("首尔", 37.5665, 126.9780, ("seoul", "首尔", "서울")),
    # Southeast Asia
    GazetteerPlace("新加坡", 1.3521, 103.8198, ("singapore", "新加坡")),
    GazetteerPlace("吉隆坡", 3.1390, 101.6869, ("kuala lumpur", "吉隆坡")),
    GazetteerPlace("曼谷", 13.7563, 100.5018, ("bangkok", "曼谷")),
    GazetteerPlace("雅加达", -6.2088, 106.8456, ("jakarta", "雅加达")),
    GazetteerPlace("马尼拉", 14.5995, 120.9842, ("manila", "马尼拉")),
    GazetteerPlace("胡志明市", 10.8231, 106.6297, ("ho chi minh", "saigon", "胡志明")),
    GazetteerPlace("河内", 21.0278, 105.8342, ("hanoi", "河内")),
    # South Asia / Middle East
    GazetteerPlace("班加罗尔", 12.9716, 77.5946, ("bangalore", "bengaluru", "班加罗尔")),
    GazetteerPlace("孟买", 19.0760, 72.8777, ("mumbai", "孟买")),
    GazetteerPlace("德里", 28.7041, 77.1025, ("delhi", "new delhi", "德里")),
    GazetteerPlace("海得拉巴", 17.3850, 78.4867, ("hyderabad", "海得拉巴")),
    GazetteerPlace("迪拜", 25.2048, 55.2708, ("dubai", "迪拜")),
    GazetteerPlace("阿布扎比", 24.4539, 54.3773, ("abu dhabi", "阿布扎比")),
    GazetteerPlace("特拉维夫", 32.0853, 34.7818, ("tel aviv", "特拉维夫")),
    # Europe
    GazetteerPlace("伦敦", 51.5074, -0.1278, ("london", "伦敦")),
    GazetteerPlace("柏林", 52.5200, 13.4050, ("berlin", "柏林")),
    GazetteerPlace("慕尼黑", 48.1351, 11.5820, ("munich", "münchen", "慕尼黑")),
    GazetteerPlace("巴黎", 48.8566, 2.3522, ("paris", "巴黎")),
    GazetteerPlace("阿姆斯特丹", 52.3676, 4.9041, ("amsterdam", "阿姆斯特丹")),
    GazetteerPlace("都柏林", 53.3498, -6.2603, ("dublin", "都柏林")),
    GazetteerPlace("苏黎世", 47.3769, 8.5417, ("zurich", "zürich", "苏黎世")),
    GazetteerPlace("华沙", 52.2297, 21.0122, ("warsaw", "华沙")),
    GazetteerPlace("克拉科夫", 50.0647, 19.9450, ("krakow", "kraków", "克拉科夫")),
    GazetteerPlace("里斯本", 38.7223, -9.1393, ("lisbon", "里斯本")),
    GazetteerPlace("马德里", 40.4168, -3.7038, ("madrid", "马德里")),
    GazetteerPlace("巴塞罗那", 41.3874, 2.1686, ("barcelona", "巴塞罗那")),
    GazetteerPlace("斯德哥尔摩", 59.3293, 18.0686, ("stockholm", "斯德哥尔摩")),
    GazetteerPlace("哥本哈根", 55.6761, 12.5683, ("copenhagen", "哥本哈根")),
    GazetteerPlace("奥斯陆", 59.9139, 10.7522, ("oslo", "奥斯陆")),
    GazetteerPlace("赫尔辛基", 60.1699, 24.9384, ("helsinki", "赫尔辛基")),
    GazetteerPlace("布拉格", 50.0755, 14.4378, ("prague", "布拉格")),
    GazetteerPlace("维也纳", 48.2082, 16.3738, ("vienna", "维也纳")),
    GazetteerPlace("佛罗伦萨", 43.7696, 11.2558, ("florence", "firenze", "佛罗伦萨")),
    GazetteerPlace("米兰", 45.4642, 9.1900, ("milan", "milano", "米兰")),
    # North America
    GazetteerPlace("旧金山", 37.7749, -122.4194, ("san francisco", "sf bay", "旧金山", "sf,")),
    GazetteerPlace("纽约", 40.7128, -74.0060, ("new york", "nyc", "纽约")),
    GazetteerPlace("西雅图", 47.6062, -122.3321, ("seattle", "西雅图")),
    GazetteerPlace("奥斯汀", 30.2672, -97.7431, ("austin", "奥斯汀")),
    GazetteerPlace("波士顿", 42.3601, -71.0589, ("boston", "波士顿")),
    GazetteerPlace("芝加哥", 41.8781, -87.6298, ("chicago", "芝加哥")),
    GazetteerPlace("洛杉矶", 34.0522, -118.2437, ("los angeles", "la", "洛杉矶")),
    GazetteerPlace("丹佛", 39.7392, -104.9903, ("denver", "丹佛")),
    GazetteerPlace("多伦多", 43.6532, -79.3832, ("toronto", "多伦多")),
    GazetteerPlace("温哥华", 49.2827, -123.1207, ("vancouver", "温哥华")),
    GazetteerPlace("蒙特利尔", 45.5017, -73.5673, ("montreal", "蒙特利尔")),
    # Latin America
    GazetteerPlace("墨西哥城", 19.4326, -99.1332, ("mexico city", "墨西哥城")),
    GazetteerPlace("圣保罗", -23.5505, -46.6333, ("sao paulo", "são paulo", "圣保罗")),
    GazetteerPlace("布宜诺斯艾利斯", -34.6037, -58.3816, ("buenos aires", "布宜诺斯艾利斯")),
    # Oceania / Africa
    GazetteerPlace("悉尼", -33.8688, 151.2093, ("sydney", "悉尼")),
    GazetteerPlace("墨尔本", -37.8136, 144.9631, ("melbourne", "墨尔本")),
    GazetteerPlace("奥克兰", -36.8485, 174.7633, ("auckland", "奥克兰")),
    GazetteerPlace("开普敦", -33.9249, 18.4241, ("cape town", "开普敦")),
    GazetteerPlace("内罗毕", -1.2921, 36.8219, ("nairobi", "内罗毕")),
)

_REMOTE_MARKERS = ("remote", "anywhere", "远程", "居家", "distributed")


def _normalize(text: str) -> str:
    return " ".join(text.lower().replace(",", " ").replace("/", " ").split())


def lookup_city(location_text: str) -> GazetteerPlace | None:
    """Resolve a public location string to a city centroid, locally.

    Remote/distributed markers intentionally resolve to nothing: a remote job
    has no honest coordinate and must stay in the unresolved bucket.
    """

    cleaned = _normalize(location_text)
    if not cleaned:
        return None
    if any(marker in cleaned for marker in _REMOTE_MARKERS):
        return None
    padded = f" {cleaned} "
    best: GazetteerPlace | None = None
    best_length = 0
    for place in _GAZETTEER:
        for alias in place.aliases:
            normalized_alias = _normalize(alias)
            if not normalized_alias:
                continue
            bounded = f" {normalized_alias} "
            if bounded in padded and len(normalized_alias) > best_length:
                best = place
                best_length = len(normalized_alias)
    return best
