class PidControl:
    def __init__(self, p_factor: float, i_factor: float, d_factor: float) -> None:
        self.previous_error = 0.0
        self.integral = 0.0
        self.p_factor = p_factor
        self.i_factor = i_factor
        self.d_factor = d_factor

    def get_next_value(self, is_value: float, target_value: float, delta_time: float) -> float:
        error = target_value - is_value
        proportional = error
        self.integral = self.integral + error * delta_time
        derivative = (error - self.previous_error) / delta_time
        control_value = (self.p_factor * proportional) \
                      + (self.i_factor * self.integral) \
                      + (self.d_factor * derivative)
        self.previous_error = error
        return is_value + control_value