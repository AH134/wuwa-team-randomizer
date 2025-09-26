<script lang="ts">
    import { changelogs } from "../data/changelogs";
</script>

<div class="inline-flex w-full flex-col">
    <div class="mb-2 text-center">
        <h2 class="text-lg">Changelogs</h2>
        <a
            href="https://github.com/AH134/wuwa-team-randomizer/blob/master/CHANGELOG.md"
            class="text-sm text-zinc-400 underline">Full changelogs</a
        >
    </div>
    <ul>
        {#each [...changelogs].reverse() as log (log.version)}
            <li
                class="mt-1.5 rounded-sm border-2 border-zinc-800 bg-zinc-900 p-1"
            >
                <p class="text-zinc-200">
                    <span class="text-lg">{log.version}</span>
                    -
                    {log.date}
                </p>
                <ul class="list-disc pl-5 text-zinc-400">
                    {#each log.changes as change}
                        <li>{change}</li>
                    {/each}
                </ul>
            </li>
        {/each}
    </ul>
</div>
