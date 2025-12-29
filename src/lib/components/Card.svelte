<script lang="ts">
    import { fly } from "svelte/transition";
    import type { CharacterCard } from "../stores/characters.svelte";

    type Props = CharacterCard & {
        mode: "readonly" | "interactive";
        delay?: number;
        onclick?: () => void;
    };

    let {
        displayName,
        weapon,
        rarity,
        attribute,
        mode,
        delay = 0,
        charSrc,
        attributeSrc,
        selected,
        weaponSrc,
        onclick,
    }: Props = $props();
    type RarityColor = {
        primary: string;
        secondary: string;
    };

    // svelte-ignore state_referenced_locally
    const rarityColor: RarityColor = {
        primary: rarity == 5 ? "bg-yellow-500" : "bg-purple-500",
        secondary: rarity == 5 ? "bg-yellow-200" : "bg-purple-200",
    };
</script>

{#snippet card()}
    <div class="relative overflow-clip">
        <div class="absolute aspect-square">
            <img
                class="h-8 w-8"
                draggable="false"
                width="32"
                height="32"
                src={attributeSrc}
                alt={attribute[0]}
            />
        </div>
        <div class="aspect-square w-full">
            <img
                class="h-full w-full object-cover"
                draggable="false"
                src={charSrc}
                alt={displayName}
            />
        </div>
        <div class="absolute bottom-0 w-full">
            <div class="relative flex w-full items-center">
                <div class="absolute -bottom-2 mt-auto h-4 w-full">
                    <div
                        class="absolute bottom-0 h-4 w-full {rarityColor.primary} blur transition-all duration-200 group-hover:h-5"
                    ></div>
                    <div
                        class="absolute bottom-0 h-2 w-full {rarityColor.secondary} blur-sm duration-200 group-hover:h-3"
                    ></div>
                </div>
            </div>
            <div class="h-0.5 {rarityColor.secondary}"></div>
        </div>
    </div>
    <div class="flex items-center justify-between overflow-hidden p-1">
        <p class="truncate">
            {displayName}
        </p>
        <img
            class="h-4 w-4 sm:h-5 sm:w-5"
            draggable="false"
            height="16"
            width="16"
            src={weaponSrc}
            alt={weapon}
        />
    </div>
{/snippet}

{#if mode == "interactive"}
    <button
        class="group relative w-24 cursor-pointer rounded border-2 border-zinc-800 bg-zinc-900 transition-all sm:w-32 {selected
            ? 'grayscale-0'
            : 'grayscale-100'}"
        type="button"
        {onclick}
    >
        {@render card()}
    </button>
{:else}
    <div
        class="group relative w-24 rounded border-2 border-zinc-800 bg-zinc-900 transition-all sm:w-32"
        in:fly|global={{
            delay: (delay + 1) * 50,
            x: -200,
        }}
    >
        {@render card()}
    </div>
{/if}
