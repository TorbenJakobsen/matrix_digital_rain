import random


class MatrixRainCharacters:
    """
    An iterator of random characters.

    >>> char_itr = MatrixRainCharacters()
    >>> print(next(char_itr))
    y
    >>> print(next(char_itr))
    l
    """

    __CHARACTERS_AS_STR: str = (
        # Western
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        # Scandinavian
        "æäøöå"
        "ÆÄØÖÅ"
        # Numbers
        "0123456789"
        # Signs and punctuations
        "~©£€#$§%^&-+=()[]{}<>|;:,.?!`@*_'\\/\""
        # Beware that hangul, katakana, and other "non-western" alphabets can leave "cruft"
    )

    __CHARACTERS_AS_LIST = list(__CHARACTERS_AS_STR)

    def __iter__(self):
        # initializes and returns the iterator object itself
        return self

    def __next__(self):
        # retrieves the next available item,
        # which is a random choice from the available characters
        return random.choice(MatrixRainCharacters.__CHARACTERS_AS_LIST)


#
#
#

if __name__ == "__main__":
    m_char_itr = MatrixRainCharacters()
    for i in range(50):
        print(next(m_char_itr))
