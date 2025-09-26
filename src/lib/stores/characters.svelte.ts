import { characters } from "../data/characters";
import { type Attribute, type Character } from "../types/types";
import { attributeNames, LOCAL_SELECTED_CHAR_KEY } from "../utils/const";
import {
    getAttributeImage,
    getCharacterImage,
    getWeaponImage,
} from "../utils/imageLoader";
import { getLocalData, setLocalData } from "../utils/local";

export interface CharacterCard extends Character {
    charSrc: string;
    attributeSrc: string;
    weaponSrc: string;
}

export interface SelectableAttribute {
    id: number;
    name: Attribute;
    src: string;
    selected: boolean;
}

class CharacterManager {
    value = $state<CharacterCard[]>([]);
    attributes = $state<SelectableAttribute[]>([]);

    selectedValue = $derived.by(() => {
        const selectedAttributes = this.attributes
            .filter((attribute) => attribute.selected)
            .map((attribute) => attribute.name);

        if (selectedAttributes.length === 0) {
            return this.value;
        }

        return this.value.filter((character) =>
            character.attribute.some((attribute) =>
                selectedAttributes.includes(attribute),
            ),
        );
    });
    isAllSelected = $derived(!this.value.some((c) => !c.selected));
    selectedIds = $derived(
        this.value.filter((c) => c.selected).map((c) => c.id),
    );

    constructor() {
        this.initializeCharacters();
        this.initializeAttributes();
        this.loadCharactersFromLocal();
    }

    private initializeCharacters() {
        this.value = characters
            .map((character) => ({
                ...character,
                charSrc: getCharacterImage(character.slug),
                attributeSrc: getAttributeImage(character.attribute[0]),
                weaponSrc: getWeaponImage(character.weapon),
            }))
            .sort((firstCharacter, secondCharacter) => firstCharacter.slug.localeCompare(secondCharacter.slug));
    }

    private initializeAttributes() {
        this.attributes = attributeNames.map((attributeName, index) => ({
            id: index,
            name: attributeName,
            src: getAttributeImage(attributeName),
            selected: false,
        }));
    }
    private loadCharactersFromLocal() {
        const localSelectedIds = getLocalData<number[]>(
            LOCAL_SELECTED_CHAR_KEY,
        );

        if (localSelectedIds?.length) {
            const idSet = new Set(localSelectedIds);
            this.value = this.value.map((character) => ({
                ...character,
                selected: idSet.has(character.id),
            }))
        }
    }

    toggleAll = () => {
        this.value = this.value.map((character) => ({
            ...character,
            selected: !this.isAllSelected,
        }));
        this.saveToLocal();
    };

    saveToLocal = () => {
        setLocalData(LOCAL_SELECTED_CHAR_KEY, this.selectedIds);
    };
}
export const selectedCharacters = new CharacterManager();
