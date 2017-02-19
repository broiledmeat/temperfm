from temperfm.profiles.profile import Profile, DEFAULT_PROFILE_PATH
default_profile = Profile(DEFAULT_PROFILE_PATH)


# noinspection PyShadowingNames
def get_tags_scores(tags, profile=default_profile):
    """
    :type tags: set[str]
    :type profile: Profile
    :rtype: tuple[float, ...]
    """
    scores = [0] * len(profile.clusters)

    for tag in tags:
        for part in tag.split():
            for i, cluster in enumerate(profile.clusters):
                if part in cluster.tags:
                    scores[i] += 1

    return scores
