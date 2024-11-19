import { render, screen, waitFor } from '@testing-library/react';
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

global.fetch = jest.fn(() =>
    Promise.resolve({
        ok: true,
        json: () => Promise.resolve([
            {
                day: 1,
                time: "10:00 AM",
                theme: "Architectural",
                locations: [
                    { lat: 51.4993, lng: -0.1273, name: "Westminster Abbey", reason: "Historic site", tips: "Arrive early" },
                ],
            },
        ]),
    })
);

describe('Results Page', () => {
    const Wrapper = ({ children }) => <ChakraProvider>{children}</ChakraProvider>;

    it('renders the page heading', () => {
        render(
            <Wrapper>
                <MapAndItineraryPage />
            </Wrapper>
        );

        expect(screen.getByRole('heading', { name: /Your Trip Itinerary/i })).toBeInTheDocument();
    });

    it('fetches and displays trip details', async () => {
        render(
            <Wrapper>
                <MapAndItineraryPage />
            </Wrapper>
        );

        await waitFor(() => {
            expect(screen.getByText(/Westminster Abbey/i)).toBeInTheDocument();
        });
    });

    it('renders map with markers and polylines after fetching data', async () => {
        render(
            <Wrapper>
                <MapAndItineraryPage />
            </Wrapper>
        );

        await waitFor(() => {
            const markers = screen.getAllByText(/Mock Marker/i);
            expect(markers.length).toBeGreaterThan(0);

            const polylines = screen.getAllByText(/Mock Polyline/i);
            expect(polylines.length).toBeGreaterThan(0);
        });
    });
});
