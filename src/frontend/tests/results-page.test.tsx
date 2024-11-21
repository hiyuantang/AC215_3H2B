import { render, screen, waitFor, act } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import MapAndItineraryPage from '@/app/results/page';

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(() => ({
    push: jest.fn(),
  })),
}));

jest.mock('@react-google-maps/api', () => ({
  GoogleMap: jest.fn(({ children }) => <div>{children}</div>),
  LoadScript: jest.fn(({ children }) => <div>{children}</div>),
  Marker: jest.fn(() => <div>Mock Marker</div>),
  Polyline: jest.fn(() => <div>Mock Polyline</div>),
}));

jest.mock('react-markdown', () => (props) => <div>{props.children}</div>);

Object.defineProperty(global, 'crypto', {
  value: {
    randomUUID: jest.fn(() => 'test-session-id'),
  },
});

global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () =>
      Promise.resolve({
        ordered_coordinates: {
          1: [[51.4993, -0.1273]],
        },
        ordered_locations: {
          1: ['Westminster Abbey'],
        },
        final_itinerary: 'Your trip summary',
      }),
  })
);

describe('Results Page', () => {
  const Wrapper = ({ children }) => <ChakraProvider>{children}</ChakraProvider>;

  it('renders the page heading', async () => {
    await act(async () => {
      render(
        <Wrapper>
          <MapAndItineraryPage />
        </Wrapper>
      );
    });

    expect(
      screen.getByRole('heading', { name: /Your Trip Itinerary/i })
    ).toBeInTheDocument();
  });

  it('fetches and displays trip details', async () => {
    await act(async () => {
      render(
        <Wrapper>
          <MapAndItineraryPage />
        </Wrapper>
      );
    });

    await waitFor(() => {
      expect(screen.getByText(/Westminster Abbey/i)).toBeInTheDocument();
    });
  });

  it('renders map with markers and polylines after fetching data', async () => {
    await act(async () => {
      render(
        <Wrapper>
          <MapAndItineraryPage />
        </Wrapper>
      );
    });

    await waitFor(() => {
      const markers = screen.getAllByText(/Mock Marker/i);
      expect(markers.length).toBeGreaterThan(0);

      const polylines = screen.getAllByText(/Mock Polyline/i);
      expect(polylines.length).toBeGreaterThan(0);
    });
  });
});
