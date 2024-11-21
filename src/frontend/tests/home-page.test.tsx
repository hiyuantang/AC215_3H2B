import { render, screen, fireEvent } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import HomePage from '@/app/page';
import { useRouter } from 'next/navigation';

jest.mock('next/navigation', () => ({
    useRouter: jest.fn(),
}));

jest.mock('react-datepicker', () => {
    const React = require('react');
    return ({ selected, onChange, placeholderText }) => (
        <input
            placeholder={placeholderText}
            value={selected ? selected.toISOString().substr(0, 10) : ''}
            onChange={(e) => onChange(new Date(e.target.value))}
        />
    );
});

describe('Home Page', () => {
    const mockPush = jest.fn();

    beforeEach(() => {
        jest.clearAllMocks();
        (useRouter as jest.Mock).mockReturnValue({ push: mockPush });
    });

    const Wrapper = ({ children }) => <ChakraProvider>{children}</ChakraProvider>;

    it('renders the heading and description', () => {
        render(
            <Wrapper>
                <HomePage />
            </Wrapper>
        );

        expect(screen.getByRole('heading', { name: /Intelligent Travel Companion/i })).toBeInTheDocument();
        expect(screen.getByText(/Plan your dream trip easily with our AI powered trip advisor/i)).toBeInTheDocument();
    });

    it('renders the form with city and trip type inputs', () => {
        render(
            <Wrapper>
                <HomePage />
            </Wrapper>
        );

        expect(screen.getByLabelText(/City/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/Type of Trip/i)).toBeInTheDocument();
    });

    it('navigates to results page on submit when all fields are filled', () => {
        render(
            <Wrapper>
                <HomePage />
            </Wrapper>
        );

        const cityInput = screen.getByLabelText(/City/i);
        fireEvent.change(cityInput, { target: { value: 'London' } });

        const tripTypeInput = screen.getByLabelText(/Type of Trip/i);
        fireEvent.change(tripTypeInput, { target: { value: 'Adventure' } });

        const startDateInput = screen.getByPlaceholderText('Start date');
        fireEvent.change(startDateInput, { target: { value: '2023-11-01' } });

        const endDateInput = screen.getByPlaceholderText('End date');
        fireEvent.change(endDateInput, { target: { value: '2023-11-05' } });

        const submitButton = screen.getByRole('button', { name: /Plan My Trip/i });
        fireEvent.click(submitButton);

        expect(mockPush).toHaveBeenCalledWith(expect.stringContaining('/results?city=London'));
    });

    it('does not go to the next page when required fields are missing', () => {
        render(
            <Wrapper>
                <HomePage />
            </Wrapper>
        );

        const submitButton = screen.getByRole('button', { name: /Plan My Trip/i });
        fireEvent.click(submitButton);

        expect(mockPush).not.toHaveBeenCalled();
    });
});
