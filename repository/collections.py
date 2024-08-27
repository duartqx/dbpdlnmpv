from pathlib import Path
from typing import override

from domain.entities import Anime, AnimeCollection
from repository import Repository
from repository.query import AnimeCollectionQuery


class AnimeCollectionRepository(Repository[AnimeCollection, AnimeCollectionQuery]):

    @override
    def insert(self, obj: AnimeCollection) -> None:
        c = self.execute(
            f"""
            INSERT INTO animeplaylist__collections
            (title, path, parent_collection_id)
            VALUES (:title, :path, :parent_collection_id)
            """,
            {
                "title": obj.title,
                "path": str(obj.path),
                "parent_collection_id": obj.parent_collection_id,
            },
        )
        obj.id = c.lastrowid

    @override
    def read(
        self, query: AnimeCollectionQuery = AnimeCollectionQuery()
    ) -> list[AnimeCollection]:
        sql = f"""
            SELECT id, title, path, watched
            FROM animeplaylist__collections
            WHERE
                deleted = :deleted
                AND parent_collection_id IS NULL
            ORDER BY title ASC
            """
        return [
            AnimeCollection(id=id, title=title, path=Path(path), watched=bool(watched))
            for id, title, path, watched in self.execute(sql, {"deleted": 0}).fetchall()
        ]

    def crawl(self, obj: Anime | AnimeCollection) -> list[Anime | AnimeCollection]:
        """
        Recursive crawler that creates collections, subcollections and anime instances
        """

        VIDEO_EXTENSIONS: tuple[str, str, str] = (
            ".mkv",
            ".mp4",
            ".webm",
        )

        objects: list[Anime | AnimeCollection] = []

        if isinstance(obj, AnimeCollection) and obj.path.is_dir():

            self.insert(obj)

            for path in obj.path.iterdir():
                objects += self.crawl(
                    AnimeCollection(
                        title=path.name, path=path, parent_collection_id=obj.id
                    )
                )
        elif (
            isinstance(obj, Anime)
            and obj.path.is_file()
            and obj.path.suffix.lower() in VIDEO_EXTENSIONS
        ):
            objects += [
                Anime(title=obj.title, path=obj.path, collection_id=obj.collection_id)
            ]

        return objects
