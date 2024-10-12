import { Progress, Text } from '@chakra-ui/react';
import { useEffect, useState } from 'react';

interface ProgressBarProps {
    title?: string;
    completeness: number;
    startDate?: Date;
}

const ProgressBar = ({ title, completeness, startDate }: ProgressBarProps) => {
    const [elapsedTimeString, setElapsedTimeString] = useState<string | null>(null);

    useEffect(() => {
        const timer = setInterval(() => {
            if (startDate) {
                const now = new Date();
                const elapsedTime = now.getTime() - startDate.getTime();

                const elapsedHours = Math.floor(elapsedTime / 3600000);
                const elapsedMinutes = Math.floor((elapsedTime % 3600000) / 60000);
                const elapsedSeconds = Math.floor((elapsedTime % 60000) / 1000);

                setElapsedTimeString(`${elapsedHours !== 0 ? `${elapsedHours}h ` : ''}${elapsedHours !== 0 || elapsedMinutes !== 0 ? `${elapsedMinutes}m ` : ''}${elapsedSeconds}s`);
            }
        }, 1000);

        return () => clearInterval(timer);
    }, [completeness, startDate]);

    const completenessPercentage = completeness * 100;

    return (
        <>
            {title && <Text fontSize={"sm"} color={"gray.500"} mb={1} textAlign={"left"}>{title}</Text>}
            <Progress
                value={completenessPercentage}
                size={"sm"}
                colorScheme='purple'
                bg={"gray.100"}
                mt={2}
                borderRadius={"2px"}
                boxShadow={"0 0 4px rgba(0, 0, 0, 0.2)"}
            />
            <Text fontSize={"sm"} color={"gray.500"} mt={2} display="flex" justifyContent="space-between">
                <span>Completion: {completenessPercentage.toFixed(1)}%</span>
                {elapsedTimeString && <span>{elapsedTimeString}</span>}
            </Text>
        </>
    );
};

export default ProgressBar;
