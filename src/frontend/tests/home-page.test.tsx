import { render, screen, fireEvent } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import HomePage from '@/app/page';
import { useRouter } from 'next/navigation';

jest.mock('next/navigation', () => ({
    useRouter: jest.fn(),
}));

jest.mock('@chakra-ui/react', () => {
    const originalModule = jest.requireActual('@chakra-ui/react');
    return {
        ...originalModule,
        useToast: jest.fn(),
    };
});

describe('Home Page', () => {
    const Wrapper = ({ children }) => <ChakraProvider>{children}</ChakraProvider>;
    const mockPush = jest.fn();
    const mockToast = jest.fn();

    beforeEach(() => {
        jest.clearAllMocks();
        (useRouter as jest.Mock).mockReturnValue({ push: mockPush });
        (jest.requireMock('@chakra-ui/react').useToast as jest.Mock).mockReturnValue(mockToast);
    });

    it('renders the heading and description', () => {
        render(
            <Wrapper>
                <HomePage />
            </Wrapper>
        );

        expect(screen.getByRole('heading', { name: /Intelligent Travel Companion/i })).toBeInTheDocument();
        expect(screen.getByText(/Plan your dream trip easily with our AI powered trip advisor/i)).toBeInTheDocument();
    });

    it('renders the form with city and trip type selectors', () => {
        render(
            <Wrapper>
                <HomePage />
            </Wrapper>
        );

        expect(screen.getByLabelText(/Select City/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/Type of Trip/i)).toBeInTheDocument();
    });

    it('navigates to results page and shows toast on submit', () => {
        render(
            <Wrapper>
                <HomePage />
            </Wrapper>
        );

        const submitButton = screen.getByRole('button', { name: /Plan My Trip/i });
        fireEvent.click(submitButton);

        expect(mockPush).toHaveBeenCalledWith('/results');
        expect(mockToast).toHaveBeenCalledWith(
            expect.objectContaining({ title: 'Planning your trip now...', status: 'success' })
        );
    });
});
