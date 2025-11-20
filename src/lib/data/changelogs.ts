export type Changelog = {
    version: string;
    date: String;
    changes: string[];
}

export const changelogs: Changelog[] = [
    {
        version: "1.2.2",
        date: "2024-06-12",
        changes: [
            "Added Character(s): Cartethyia"
        ]
    },
    {
        version: "1.2.3",
        date: "2025-07-05",
        changes: [
            "Added Character(s): Lupa"
        ]
    },
    {
        version: "1.2.4",
        date: "2025-09-25",
        changes: [
            "Added Character(s): Iuno, Augusta, and Phrolova",
            "Sort characters alphabetically",
        ]
    },
    {
        version: "1.2.5",
        date: "2025-10-21",
        changes: [
            "Added Character(s): Galbrena, Qiuyuan",
        ]
    },
    {
        version: "1.2.6",
        date: "2025-11-20",
        changes: [
            "Added Character(s): Chisa, Buling",
        ]
    },
];
