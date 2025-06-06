
from character_helpers import (
    characters_extraction,
    retrieve_character_history,
    verify_character_consistency,
    recommend_character_interactions
)

from typing import Dict, List, Tuple

class CharacterAgent:
    def __init__(self, client, vector_metadata, num_scenes=1):
        self.client = client
        self.vector_metadata = vector_metadata
        self.num_scenes = num_scenes
        self.internal_thoughts = []  # Tracks internal reasoning

    def think(self, scene_description: str, scene_number: int) -> Dict:
        """
        Think step: Analyze the scene to detect characters and show prior context range.
        """
        start_scene = max(1, scene_number - self.num_scenes)
        scene_range = list(range(start_scene, scene_number))
        print(f"📚 Retrieving script metadata for scene(s): {scene_range}")

        character_info = characters_extraction(
            client=self.client,
            scene_description=scene_description,
            prior_scene_metadata=self.vector_metadata,
            scene_number=scene_number,
            num_scenes=self.num_scenes
        )
        self.internal_thoughts.append(f"Think: Identified characters {character_info['current_scene_characters']} using context from scene(s) {scene_range}.")
        return character_info

    def act(self, character_info: Dict, scene_description: str, scene_number: int) -> Dict[str, Dict]:
        """
        Act step: Retrieve character histories from previous scenes.
        """
        character_histories = {}
        for character in character_info["current_scene_characters"]:
            profile = retrieve_character_history(
                client=self.client,
                character=character,
                vector_metadata=self.vector_metadata,
                current_scene_description=scene_description,
                num_scenes=self.num_scenes
            )
            character_histories[character] = profile
        self.internal_thoughts.append(f"Act: Retrieved profiles for {list(character_histories.keys())}.")
        return character_histories

    def observe(self, character_histories: Dict[str, Dict], scene_description: str) -> Tuple[bool, str]:
        """
        Observe step: Verify if characters are consistent with their profiles.
        """
        is_consistent, explanation = verify_character_consistency(
            client=self.client,
            character_profiles=character_histories,
            scene_description=scene_description,
            num_scenes=self.num_scenes
        )
        verdict = "consistent" if is_consistent else "inconsistent"
        self.internal_thoughts.append(f"Observe: Scene is {verdict}.")
        return is_consistent, explanation

    def recommend(self, character_histories: Dict[str, Dict], scene_description: str, is_consistent: bool, explanation: str) -> str:
        """
        Recommend step: Suggest how to maximize character interactions, or fix inconsistencies.
        """
        recommendation = recommend_character_interactions(
            client=self.client,
            character_profiles=character_histories,
            scene_description=scene_description,
            num_scenes=self.num_scenes,
            is_consistent=is_consistent,
            consistency_result=explanation
        )
        self.internal_thoughts.append("Recommend: Provided suggestions for enhancing character dynamics.")
        return recommendation

    def run(self, scene_description: str, scene_number: int) -> Tuple[Dict[str, Dict], bool, str, str, List[str]]:
        """
        Full ReAct cycle: Think ➔ Act ➔ Observe ➔ Recommend

        Returns:
            - character_histories (dict)
            - is_consistent (bool)
            - explanation (str)
            - recommendations (str)
            - internal_thoughts (list of str)
        """
        character_info = self.think(scene_description, scene_number)
        character_histories = self.act(character_info, scene_description, scene_number)
        is_consistent, explanation = self.observe(character_histories, scene_description)
        recommendations = self.recommend(character_histories, scene_description, is_consistent, explanation)
        return character_histories, is_consistent, explanation, recommendations, self.internal_thoughts
