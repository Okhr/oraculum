import { Progress, Text } from '@chakra-ui/react';

interface ProgressBarProps {
    title?: string;
    completeness: number;
    startDate?: Date;
}

const ProgressBar = ({ title, completeness, startDate }: ProgressBarProps) => {
    let remainingTimeString = null

    if (startDate) {
        const now = new Date();
        const elapsedTime = now.getTime() - startDate.getTime();
        let remainingTime = ((1 - completeness) / completeness) * elapsedTime;

        // Add a multiplicator factor on the remaining time that is dependant on the percentage
        const multiplicatorFactor = 1 + (2 - 2 * completeness);
        remainingTime *= multiplicatorFactor;

        if (remainingTime !== null && remainingTime !== Infinity && remainingTime > 0) {
            const hours = Math.floor(remainingTime / 3600000);
            const minutes = Math.floor((remainingTime % 3600000) / 60000);
            const seconds = Math.floor((remainingTime % 60000) / 1000);

            remainingTimeString = `${hours !== 0 ? `${hours}h ` : ''}${hours !== 0 || minutes !== 0 ? `${minutes}m ` : ''}${seconds}s`;
        }
    }

    const completenessPercentage = completeness * 100;

    return (
        <>
            {title && <Text fontSize={"sm"} color={"gray.500"} mb={1} textAlign={"left"}>{title}</Text>}
            <Progress
                value={completenessPercentage}
                size={"sm"}
                colorScheme='purple'
                bg={"gray.100"}
                borderRadius={"2px"}
                boxShadow={"0 0 4px rgba(0, 0, 0, 0.2)"}
            />
            <Text fontSize={"sm"} color={"gray.500"} mt={1} display="flex" justifyContent="space-between">
                <span>Completion: {completenessPercentage.toFixed(1)}%</span>
                {remainingTimeString && <span>{remainingTimeString}</span>}
            </Text>
        </>
    );
};

export default ProgressBar;
