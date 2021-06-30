from cm4twc.component import SurfaceLayerComponent
try:
    from .dummyfortran import dummyfortran
except ImportError:
    # since dummyfortran is not defined in this exception catch, it will raise
    # a NameError later if DummyFortran component is used, but other component
    # will remain usable
    pass
try:
    from .dummyc import dummyc
except ImportError:
    # since dummyc is not defined in this exception catch, it will raise
    # a NameError later if DummyC component is used, but other component
    # will remain usable
    pass


class Dummy(SurfaceLayerComponent):
    # supersede existing inwards/outwards for physically meaningless ones
    _inwards_info = {
        'transfer_k': {
            'units': '1',
            'from': 'subsurface',
            'method': 'mean'
        },
        'transfer_l': {
            'units': '1',
            'from': 'openwater',
            'method': 'mean'
        },
        'transfer_n': {
            'units': '1',
            'from': 'openwater',
            'method': 'mean'
        }
    }
    _outwards_info = {
        'transfer_i': {
            'units': '1',
            'to': ['subsurface'],
            'method': 'mean'
        },
        'transfer_j': {
            'units': '1',
            'to': ['openwater'],
            'method': 'mean'
        }
    }
    # define some dummy inputs/parameters/constants/states/outputs
    _inputs_info = {
        'driving_a': {
            'units': '1',
            'kind': 'dynamic'
        },
        'driving_b': {
            'units': '1',
            'kind': 'dynamic'
        },
        'driving_c': {
            'units': '1',
            'kind': 'dynamic'
        },
        'ancillary_c': {
            'units': '1',
            'kind': 'static'
        }
    }
    # _parameters_info = {}
    # _constants_info = {}
    _states_info = {
        'state_a': {
            'units': '1',
            'divisions': 1
        },
        'state_b': {
            'units': '1',
            'divisions': 1
        }
    }
    _outputs_info = {
        'output_x': {
            'units': '1'
        }
    }
    _solver_history = 1
    _requires_land_sea_mask = True
    _requires_flow_direction = True

    def initialise(self,
                   # component states
                   state_a, state_b,
                   **kwargs):

        state_a[-1][:] = 0
        state_b[-1][:] = 0

    def run(self,
            # from exchanger
            transfer_k, transfer_l, transfer_n,
            # component driving data
            driving_a, driving_b, driving_c,
            # component ancillary data
            ancillary_c,
            # component parameters
            # component states
            state_a, state_b,
            # component constants
            **kwargs):

        state_a[0][:] = state_a[-1] + 1
        state_b[0][:] = state_b[-1] + 2

        output_x, _ = self.spacedomain.route(driving_a + driving_b + driving_c
                                             + transfer_n - state_a[0])

        return (
            # to exchanger
            {
                'transfer_i':
                    driving_a + driving_b + transfer_l + ancillary_c * state_a[0],
                'transfer_j':
                    driving_a + driving_b + driving_c + transfer_k + state_b[0]
            },
            # component outputs
            {
                'output_x':
                    output_x
            }
        )

    def finalise(self,
                 # component states
                 state_a, state_b,
                 **kwargs):
        pass


class DummyFortran(Dummy):
    # overwrite states to explicitly set array order
    _states_info = {
        'state_a': {
            'units': '1',
            'divisions': 1,
            'order': 'F'
        },
        'state_b': {
            'units': '1',
            'divisions': 1,
            'order': 'F'
        }
    }

    def initialise(self,
                   # component states
                   state_a, state_b,
                   **kwargs):
        dummyfortran.initialise(state_a[-1], state_b[-1])

    def run(self,
            # from exchanger
            transfer_k, transfer_l, transfer_n,
            # component driving data
            driving_a, driving_b, driving_c,
            # component ancillary data
            ancillary_c,
            # component parameters
            # component states
            state_a, state_b,
            # component constants
            **kwargs):

        transfer_i, transfer_j, output_x = dummyfortran.run(
            transfer_k, transfer_l, transfer_n,
            driving_a, driving_b, driving_c,
            ancillary_c,
            state_a[-1], state_a[0], state_b[-1], state_b[0]
        )

        output_x, _ = self.spacedomain.route(output_x)

        return (
            # to exchanger
            {
                'transfer_i': transfer_i,
                'transfer_j': transfer_j
            },
            # component outputs
            {
                'output_x': output_x
            }
        )

    def finalise(self,
                 # component states
                 state_a, state_b,
                 **kwargs):
        dummyfortran.finalise()


class DummyC(Dummy):

    def initialise(self,
                   # component states
                   state_a, state_b,
                   **kwargs):
        dummyc.initialise(state_a[-1], state_b[-1])

    def run(self,
            # from exchanger
            transfer_k, transfer_l, transfer_n,
            # component driving data
            driving_a, driving_b, driving_c,
            # component ancillary data
            ancillary_c,
            # component parameters
            # component states
            state_a, state_b,
            # component constants
            **kwargs):

        transfer_i, transfer_j, output_x = dummyc.run(
            transfer_k, transfer_l, transfer_n,
            driving_a, driving_b, driving_c,
            ancillary_c,
            state_a[-1], state_a[0], state_b[-1], state_b[0]
        )

        output_x, _ = self.spacedomain.route(output_x)

        return (
            # to exchanger
            {
                'transfer_i': transfer_i,
                'transfer_j': transfer_j
            },
            # component outputs
            {
                'output_x': output_x
            }
        )

    def finalise(self,
                 # component states
                 state_a, state_b,
                 **kwargs):
        dummyc.finalise()
