extends RefCounted

## Injury tiers per body region. Each tier is the highest damage value that
## still selects that injury, so a hit uses the first threshold at or above it.
const INJURIES := {
    "head": {
        18: "Chichón",
        20: "Ojo negro",
        35: "Viene el ratón Pérez!",
        50: "Tabique roto",
        75: "Contusión",
        90: "Fractura de mandíbula",
        100: "Hemorragia cerebral",
    },
    "torso": {
        18: "Moretón",
        30: "Corte",
        40: "Hernia abdominal",
        60: "Fractura de esternón",
        75: "Hemotórax",
        85: "Fractura de costilla",
        100: "Sangrado interno",
    },
    "upper": {
        18: "Raspón",
        20: "Moretón",
        35: "Contusión muscular",
        45: "Dislocación de hombro",
        60: "Fractura incompleta",
        75: "Fractura",
        100: "Fractura expuesta",
    },
    "forearm": {
        18: "Raspón",
        20: "Moretón",
        35: "Tendinitis",
        45: "Dislocación de codo",
        60: "Fractura en tallo verde",
        75: "Fractura",
        100: "Fractura expuesta",
    },
    "hand": {
        18: "Raspón",
        20: "Moretón",
        30: "Esguince de muñeca",
        45: "Luxación de dedo",
        60: "Fractura de metacarpiano",
        75: "Fractura de muñeca",
        90: "Desgarro de tendón",
        100: "Fractura expuesta",
    },
    "hips": {
        18: "Moretón",
        25: "Laceración",
        40: "Desgarro del flexor de cadera",
        55: "Chau bolas!",
        70: "Cadera dislocada",
        85: "Fractura de cuello femoral",
        100: "Fractura de pelvis",
    },
    "thigh": {
        18: "Moretón",
        20: "Raspón",
        30: "Laceración",
        40: "Desgarre",
        50: "Esguince de ligamento colateral medial",
        65: "Dislocación de rótula",
        75: "Rotura de menisco",
        85: "Rotura de ligamento cruzado anterior",
        95: "Fractura de fémur",
        100: "Fractura abierta de fémur",
    },
    "shin": {
        18: "Moretón",
        20: "Raspón",
        30: "Laceración",
        40: "Hematoma óseo",
        55: "Fractura de peroné",
        70: "Fractura de tibia",
        85: "Síndrome compartimental",
        100: "Fractura abierta de tibia",
    },
    "foot": {
        18: "Moretón",
        20: "Ampolla",
        30: "Esguince leve de tobillo",
        45: "Hematoma subungueal",
        60: "Fractura de dedo del pie",
        75: "Fractura de metatarsiano",
        90: "Rotura del tendón de Aquiles",
        100: "Fractura abierta de tobillo",
    },
}

## Skeleton bone names, without their left/right suffix, mapped to a region.
const REGION_BY_BONE := {
    "head": "head",
    "torso": "torso",
    "arm": "upper",
    "forearm": "forearm",
    "hand": "hand",
    "hip": "hips",
    "leg": "thigh",
    "shin": "shin",
    "foot": "foot",
}

## Returns the injury region for a skeleton bone such as "Forearm.R".
static func get_region_for_bone(bone_name: String) -> String:
    var base_name := bone_name.get_slice(".", 0).to_lower()
    return REGION_BY_BONE.get(base_name, "torso")

## Returns the injury whose tier is the first one at or above `damage`.
## Damage above the last tier uses the most severe injury.
static func get_injury(region: String, damage: float) -> String:
    var tiers: Dictionary = INJURIES.get(region, INJURIES["torso"])
    var thresholds := tiers.keys()
    thresholds.sort()

    for threshold in thresholds:
        if damage <= float(threshold):
            return tiers[threshold]

    return tiers[thresholds[thresholds.size() - 1]]
