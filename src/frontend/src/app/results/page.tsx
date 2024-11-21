'use client';

import {
    Box, Heading, Text, VStack, Button
} from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { GoogleMap, LoadScript, Marker, Polyline } from "@react-google-maps/api";
import { useRouter } from 'next/navigation';

const generateSessionId = () => {
    return crypto.randomUUID();
};

const fetchIntegratedResponse = async (queryParams, sessionId) => {
    try {
        const response = await fetch('http://localhost:9000/llm-sf/integrated-response', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Session-ID': sessionId
            },
            body: JSON.stringify(queryParams)
        });
        if (!response.ok) {
            throw new Error('Failed to fetch integrated response');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching integrated response:', error);
        return null;
    }
};

const calculateCenter = (coordinates) => {
    const latSum = coordinates.reduce((sum, loc) => sum + loc[0], 0);
    const lngSum = coordinates.reduce((sum, loc) => sum + loc[1], 0);
    return { lat: latSum / coordinates.length, lng: lngSum / coordinates.length };
};

const containerStyle = { width: '100%', height: '100%' };

export default function MapAndItineraryPage() {
    const router = useRouter();
    const [tripDetails, setTripDetails] = useState([]);
    const [finalMessage, setFinalMessage] = useState('');
    const [center, setCenter] = useState({ lat: 51.4993, lng: -0.1273 });
    const [sessionId] = useState(generateSessionId);
    const [selectedDay, setSelectedDay] = useState(null);

    useEffect(() => {
        async function fetchData() {
            const params = {
                city: new URLSearchParams(window.location.search).get('city'),
                days: new URLSearchParams(window.location.search).get('days'),
                type: new URLSearchParams(window.location.search).get('type'),
                month: new URLSearchParams(window.location.search).get('month'),
            };

            const data = await fetchIntegratedResponse(params, sessionId);
            if (data && data.ordered_coordinates) {
                const allCoordinates = Object.values(data.ordered_coordinates).flat();
                setTripDetails(data);
                setCenter(calculateCenter(allCoordinates));
                setFinalMessage(data.final_itinerary || '');
                setSelectedDay(Object.keys(data.ordered_coordinates)[0]);
            }
        }
        fetchData();
    }, [sessionId]);

    return (
        <Box className="min-h-screen" display="flex" flexDirection="column" bg="gray.50" p="10" minHeight="100vh">
            <Heading as="h1" size="2xl" fontWeight="extrabold" mb={6} bgGradient="linear(to-r, orange.500, red.500)" bgClip="text" textAlign="center">
                Your Trip Itinerary
            </Heading>
            <Box display="flex" flexGrow="1" justifyContent="center" alignItems="center">
                <Box width="50%" bg="white" shadow="2xl" rounded="xl" p="6" mr="8" display="flex" justifyContent="center" alignItems="center" height="500px">
                    <LoadScript googleMapsApiKey={process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}>
                        <GoogleMap mapContainerStyle={containerStyle} center={center} zoom={12}>
                            {selectedDay && tripDetails?.ordered_coordinates[selectedDay]?.map((coord, index) => (
                                <Marker key={`${selectedDay}-${index}`} position={{ lat: coord[0], lng: coord[1] }} />
                            ))}
                            {selectedDay && (
                                <Polyline path={tripDetails?.ordered_coordinates[selectedDay]?.map(coord => ({ lat: coord[0], lng: coord[1] }))} options={{
                                    strokeColor: '#FF8C00',
                                    strokeOpacity: 0.8,
                                    strokeWeight: 4
                                }} />
                            )}
                        </GoogleMap>
                    </LoadScript>
                </Box>
                <Box width="35%" height="500px" bg="white" shadow="2xl" rounded="xl" p="6" overflowY="auto">
                    <VStack spacing={6} align="stretch">
                        {Object.entries(tripDetails?.ordered_locations || {}).map(([day, locations]) => (
                            <Box key={day} p={4} bg={selectedDay === day ? "orange.100" : "gray.100"} rounded="md" onClick={() => setSelectedDay(day)} cursor="pointer">
                                <Heading as="h3" size="lg" mb={3} color="orange.500">Day {day}</Heading>
                                <ul>
                                    {locations.map((location, index) => (
                                        <li key={index}>
                                            <Text fontSize="md" fontWeight="bold">{location}</Text>
                                        </li>
                                    ))}
                                </ul>
                            </Box>
                        ))}
                    </VStack>
                </Box>
            </Box>
            {finalMessage && (
                <Box mt={6} p={4} bg="white" shadow="2xl" rounded="xl" textAlign="center">
                    <Heading as="h2" size="lg" mb={4} color="orange.500">Final Itinerary Summary</Heading>
                    <Text fontSize="md" color="gray.600">{finalMessage}</Text>
                </Box>
            )}
            <Button bgGradient="linear(to-r, orange.400, red.400)" color="white" size="lg" _hover={{ bgGradient: "linear(to-r, orange.500, red.500)" }} alignSelf="center" mt={4} onClick={() => router.push('/')}>
                Back to Home
            </Button>
        </Box>
    );
}
