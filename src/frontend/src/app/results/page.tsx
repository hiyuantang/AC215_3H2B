'use client';

import {
    Box, Heading, Text, VStack, Button
} from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { GoogleMap, LoadScript, Marker, Polyline } from "@react-google-maps/api";
import { useRouter } from 'next/navigation';

const getTripDetails = async () => {
    try {
        const response = await fetch('/api/trip-details');
        if (!response.ok) {
            throw new Error('Failed to fetch trip details');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching trip details:', error);
        return [];
    }
};

// Calculate center of multiple coordinates
const calculateCenter = (locations) => {
    const latSum = locations.reduce((sum, loc) => sum + loc.lat, 0);
    const lngSum = locations.reduce((sum, loc) => sum + loc.lng, 0);
    return { lat: latSum / locations.length, lng: lngSum / locations.length };
};

const containerStyle = { width: '100%', height: '100%' };

export default function MapAndItineraryPage() {
    const router = useRouter();
    const [tripDetails, setTripDetails] = useState([]);
    const [center, setCenter] = useState({ lat: 51.4993, lng: -0.1273 });

    useEffect(() => {
        async function fetchData() {
            const details = await getTripDetails();
            setTripDetails(details);
            const allLocations = details.flatMap(day => day.locations);
            setCenter(calculateCenter(allLocations));
        }
        fetchData();
    }, []);

    return (
        <Box className="min-h-screen" display="flex" flexDirection="column" bg="gray.50" p="10" minHeight="100vh">
            <Heading as="h1" size="2xl" fontWeight="extrabold" mb={6} bgGradient="linear(to-r, orange.500, red.500)" bgClip="text" textAlign="center">
                Your Trip Itinerary
            </Heading>
            <Box display="flex" flexGrow="1" justifyContent="center" alignItems="center">
                <Box width="50%" bg="white" shadow="2xl" rounded="xl" p="6" mr="8" display="flex" justifyContent="center" alignItems="center" height="500px">
                    <LoadScript googleMapsApiKey={process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}>
                        <GoogleMap mapContainerStyle={containerStyle} center={center} zoom={12}>
                            {tripDetails.map(day => day.locations.map((location, index) => (
                                <Marker key={`${day.day}-${index}`} position={{ lat: location.lat, lng: location.lng }} label={location.name} />
                            )))}
                            {tripDetails.map(day => (
                                <Polyline key={day.day} path={day.locations.map(loc => ({ lat: loc.lat, lng: loc.lng }))} options={{
                                    strokeColor: '#FF8C00',
                                    strokeOpacity: 0.8,
                                    strokeWeight: 4
                                }} />
                            ))}
                        </GoogleMap>
                    </LoadScript>
                </Box>
                <Box width="35%" height="500px" bg="white" shadow="2xl" rounded="xl" p="6" overflowY="auto">
                    <VStack spacing={6} align="stretch">
                        {tripDetails.map((day, index) => (
                            <Box key={index} p={4} bg="gray.100" rounded="md">
                                <Heading as="h3" size="lg" mb={3} color="orange.500">Day {day.day}: {day.theme}</Heading>
                                <Text fontWeight="bold" color="gray.600">Recommended Start Time: {day.time}</Text>
                                {day.locations.map((location, locIndex) => (
                                    <Box key={locIndex} mt={2}>
                                        <Text fontSize="md" fontWeight="bold" mb={1}>{location.name}</Text>
                                        <Text fontSize="sm">Reason: {location.reason}</Text>
                                        <Text fontSize="sm">Tips: {location.tips}</Text>
                                    </Box>
                                ))}
                            </Box>
                        ))}
                    </VStack>
                </Box>
            </Box>
            <Button bgGradient="linear(to-r, orange.400, red.400)" color="white" size="lg" _hover={{ bgGradient: "linear(to-r, orange.500, red.500)" }} alignSelf="center" onClick={() => router.push('/')}>
                Back to Home
            </Button>
        </Box>
    );
}
