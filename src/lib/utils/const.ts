import type { Attribute, Gender, Rarity, Weapon } from "../types/types";

export const LOCAL_SELECTED_CHAR_KEY = "selectedCharacters";

export const MAX_TEAM_COUNT = 10;

export const MIN_TEAM_COUNT = 1;

export const weaponNames: Weapon[] = [
    "broadblade",
    "gauntlet",
    "sword",
    "pistol",
    "rectifier",
];

export const attributeNames: Attribute[] = [
    "fusion",
    "glacio",
    "aero",
    "electro",
    "spectro",
    "havoc",
];

export const rarity: Rarity[] = [4, 5];

export const genders: Gender[] = ["male", "female"];
