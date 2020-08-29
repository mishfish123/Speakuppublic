
from .api_types import ApiCall

API_BASE_URL = "http://www.openaustralia.org/api"

__version__ = "1.0.1"

__all__ = [
    "OpenAustralia"
]


class OpenAustralia:
    """ Client for OpenAustralia API.

    Provides an implementation for the REST api given at:
        http://www.openaustralia.org.au/api

    :param api_key: API Access key
                    (http://www.openaustralia.org.au/api/key)
    :type api_key: string

    :param api_url: API url endpoint. Defaults to API_BASE_URL,
                    but can be switched out (eg. point at your
                    own instance for testing).
    :type api_url: string
    """

    API_VERSION = __version__

    class House:
        representatives = 'representatives'
        senate = 'senate'

    def __init__(self, api_key, api_url=API_BASE_URL):
        self.api_key = api_key
        self.api_url = api_url
        if not api_url or not api_key:
            raise ValueError('Invalid parameters')
        if self.api_url.endswith('/'):
            self.api_url = self.api_url[:-1]

    def _oa_call(self, function, **kwargs):
        return ApiCall(
            self.api_url,
            self.api_key, function,
            **kwargs
        ).result

    def get_divisions(self, postcode=None, date=None, search=None):
        """ Fetch a list of electoral divisions.

        **Arguments:**

        :param postcode: (optional) Fetch the list of electoral divisions
                that are within the given postcode (there can be more
                than one)

        :param date: (optional) Fetch the list of electoral divisions as
                it was on this date.

        :param search: (optional) Fetch the list of electoral divisions
                that match this search string
        """
        return self._oa_call(
            "getDivisions", postcode=postcode, date=date, search=search
        )

    def get_representative(
        self, person_id=None, division=None, always_return=None
    ):
        """ Fetch a particular member of the House of Representatives.

        **Arguments:**

        :param person_id: (optional) If you know the person ID for the member
                you want (returned from getRepresentatives or
                elsewhere), this will return data for that person.

        :param division: (optional) The name of an electoral division;
                we will try and work it out from whatever you
                give us. :)

        :param always_return: (optional) For the division option,
                sets whether to always try and return a Representative,
                even if the seat is currently vacant.
        """
        return self._oa_call(
            "getRepresentative",
            id=person_id, division=division, always_return=always_return
        )

    def get_representatives(
        self, postcode=None, data=None, party=None, search=None
    ):
        """ Fetch a list of members of the House of Representatives.

        **Arguments:**

        :param postcode: (optional) Fetch the list of Representatives whose
                electoral division lies within the postcode (there may be
                more than one)

        :param date: (optional) Fetch the list of members of the House of
                Representatives as it was on this date.

        :param party: (optional) Fetch the list of Representatives from
                the given party.

        :param search: (optional) Fetch the list of Representatives that
                match this search string in their name.
        """
        return self._oa_call(
            "getRepresentatives",
            postcode=postcode, data=data, party=party, search=search
        )

    def get_senator(self, person_id):
        """ Fetch a particular Senator.

        **Arguments:**

        :param person_id: (required) If you know the person ID for the Senator
                you want, this will return data for that person.
        """
        return self._oa_call(
            "getSenator", id=person_id
        )

    def get_senators(self, date=None, party=None, state=None, search=None):
        """ Fetch a list of Senators.

        **Arguments:**

        :param date: (optional) Fetch the list of Senators as it was on this
                date.__version__

        :param party: (optional) Fetch the list of Senators from the given
                party.

        :param state: (optional) Fetch the list of Senators from the given
                state. (NSW, Tasmania, WA, Queensland, Victoria, SA, NT, ACT)

        :param search: (optional) Fetch the list of Senators that match this
                search string in their name.
        """
        return self._oa_call(
            "getSenators",
            date=date, party=party, state=state, search=search
        )

    def get_debates(
        self, debate_type, date=None, search=None, person_id=None,
        gid=None, year=None, order=None, page=None, num=None
    ):
        """ Fetch Debates.

        This includes Oral Questions.

        **Arguments:**

        :param debate_type: (required) One of "representatives" or "senate".

        Note you can only supply one of the following search terms at present.

        :param date: Fetch the debates for this date.

        :param search: Fetch the debates that contain this term.

        :param person_id: Fetch the debates by a particular person ID.

        :param gid: Fetch the speech or debate that matches this GID.

        :param year: (Undocumented. Seems to return dates of debates, for
                matching year.)

        Result filtering:

        :param order: (optional, when using search or person)
                d for date ordering, r for relevance ordering.

        :param page: (optional, when using search or person) Page of results
                to return.

        :param num: (optional, when using search or person) Number of results
                to return.
        """
        if not debate_type or debate_type.lower() not in (
            'representatives', 'senate'
        ):
            raise ValueError("Invalid debate_type: {}".format(debate_type))

        if not (date or search or person_id or gid or year):
            raise ValueError("At least one type of search must be given")

        return self._oa_call(
            "getDebates",
            type=debate_type.lower(), date=date, search=search,
            person=person_id, gid=gid, year=year, order=order,
            page=page, num=num
        )

    def get_hansard(
        self, search=None, person_id=None, order=None, page=None, num=None
    ):
        """ Fetch all Hansard.

        **Arguments:**

        Note you can only supply one of the following at present.

        :param search: Fetch the data that contain this term.

        :param person_id: Fetch the data by a particular person ID.

        Result filtering:

        :param order: (optional, when using search or person, defaults to date)
                d for date ordering, r for relevance ordering, p for use by
                person.

        :param page: (optional, when using search or person) Page of results
                to return.

        :param num: (optional, when using search or person) Number of results
                to return.
        """
        return self._oa_call(
            "getHansard",
            search=search, person=person_id,
            order=order, page=page, num=num
        )

    def get_comments(
        self, date=None, search=None, user_id=None, pid=None,
        page=None, num=None
    ):
        """ Fetch comments left on OpenAustralia.

        With no arguments, returns most recent comments in reverse date order.

        **Arguments:**

        :param date: (optional) Fetch the comments for this date.

        :param search: (optional) Fetch the comments that contain this term.

        :param user_id: (optional) Fetch the comments by a particular user ID.

        :param pid: (optional) Fetch the comments made on a particular
                person ID (Representative/Senator).

        :param page: (optional) Page of results to return.

        :param num: (optional) Number of results to return.
        """
        return self._oa_call(
            "getComments",
            date=date, search=search, user_id=user_id, pid=pid,
            page=page, num=num
        )
