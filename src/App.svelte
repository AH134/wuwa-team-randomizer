<script lang="ts">
    import Card from "./lib/components/Card.svelte";
    import DisplayContainer from "./lib/components/DisplayContainer.svelte";
    import {
        selectedCharacters,
        type CharacterCard,
    } from "./lib/stores/characters.svelte";
    import { shuffle } from "./lib/utils/shuffle";
    import { MAX_RANDOMIZED_CHARACTERS } from "./lib/utils/const";
    import AttributeButton from "./lib/components/AttributeButton.svelte";
    import Changelog from "./lib/components/Changelog.svelte";

    let randomizedCharacters: CharacterCard[] = $state([]);

    const generateRandomizedCharacters = () => {
        randomizedCharacters = [];
        const selectableCharacters = selectedCharacters.value.filter(
            (character) => character.selected,
        );

        if (selectableCharacters.length <= 0) {
            return;
        }

        const length = Math.min(
            selectableCharacters.length,
            MAX_RANDOMIZED_CHARACTERS,
        );

        randomizedCharacters = shuffle(selectableCharacters, length);
    };
</script>

<header class="mb-8 text-center">
    <a
        class="text-sm text-zinc-300 hover:text-zinc-200 md:text-base"
        href="https://github.com/ah134/wuthering-waves-team-randomizer"
        target="_blank">Github Repository</a
    >

    <h1 class="text-xl text-zinc-100 md:text-3xl">
        Wuthering Waves Team Randomizer
    </h1>
</header>

<main class="p-2">
    <div class="flex flex-wrap justify-center gap-3 align-middle">
        {#key randomizedCharacters}
            {#each [0, 3, 6] as start (start)}
                <DisplayContainer
                    randomizedCharacters={randomizedCharacters.slice(
                        start,
                        start + 3,
                    )}
                />
            {/each}
        {/key}
    </div>
    <div class="mt-4 flex flex-wrap justify-center gap-2 sm:grid-cols-3">
        <button
            class="h-12 w-28 cursor-pointer rounded-md border-2 border-zinc-800 bg-zinc-950 p-1 transition-all hover:bg-zinc-900"
            onclick={selectedCharacters.toggleAll}
            >{selectedCharacters.isAllSelected
                ? "Deselect all"
                : "Select all"}</button
        >
        <button
            class="h-12 w-36 cursor-pointer rounded-tl-md rounded-br-md bg-zinc-100 p-1 text-zinc-900 transition-all hover:bg-white"
            onclick={generateRandomizedCharacters}>Generate teams</button
        >
        <button
            class="h-12 w-28 cursor-pointer rounded-md border-2 border-zinc-800 bg-zinc-950 p-1 transition-all hover:bg-zinc-900"
            onclick={() => {
                randomizedCharacters = [];
            }}>Reset</button
        >
    </div>

    <div class="mt-4 mb-4 flex flex-wrap justify-center gap-1">
        {#each selectedCharacters.attributes as attribute (attribute.id)}
            <AttributeButton
                attribute={attribute.name}
                selected={attribute.selected}
                src={attribute.src}
                onclick={() => {
                    attribute.selected = !attribute.selected;
                }}
            />
        {/each}
    </div>

    <div class="flex flex-wrap justify-center gap-2">
        {#each selectedCharacters.selectedValue as char (char.id)}
            <Card
                {...char}
                mode="interactive"
                selected={char.selected}
                onclick={() => {
                    char.selected = !char.selected;
                    selectedCharacters.saveToLocal();
                }}
            />
        {/each}
    </div>

    <div class="mx-auto mt-8 max-w-3xl">
        <Changelog />
    </div>
</main>
